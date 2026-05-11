"""
商业计划书生成节点
基于技术分析和商业化评估结果，生成专业的商业计划书
"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import BPGenerationInput, BPGenerationOutput


def bp_generation_node(
    state: BPGenerationInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> BPGenerationOutput:
    """
    title: 商业计划书生成
    desc: 基于技术分析和商业化评估结果，生成专业的商业计划书（BP），包括项目概述、技术优势、市场分析、商业模式、融资计划等
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 从config的metadata读取LLM配置路径
    llm_cfg_path = config.get('metadata', {}).get('llm_cfg', 'config/bp_generation_llm_cfg.json')
    cfg_file = os.path.join(os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects'), llm_cfg_path)
    
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get('config', {})
    sp = _cfg.get('sp', '')
    up = _cfg.get('up', '')
    
    # 序列化数据
    tech_analysis_str = json.dumps(state.tech_analysis, ensure_ascii=False, indent=2)
    commercial_str = json.dumps(state.commercial_potential, ensure_ascii=False, indent=2)
    
    # 使用jinja2模板渲染提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        'tech_analysis': tech_analysis_str,
        'commercial_potential': commercial_str,
        'user_type': state.user_type
    })
    
    # 初始化LLM客户端
    client = LLMClient()
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]
    
    # 调用大模型 - 使用较高的max_tokens来支持长文本生成
    response = client.invoke(
        messages=messages,
        model=llm_config.get('model', 'doubao-seed-2-0-pro-260215'),
        temperature=llm_config.get('temperature', 0.7),
        max_completion_tokens=llm_config.get('max_completion_tokens', 8192)
    )
    
    # 处理响应内容
    content = response.content
    if isinstance(content, str):
        bp_document = content.strip()
    else:
        bp_document = str(content)
    
    return BPGenerationOutput(bp_document=bp_document)
