"""
政策检索节点
检索与该技术相关的国家/地方政策支持，包括资金补贴、税收优惠、人才引进等
"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import PolicySearchInput, PolicySearchOutput


def policy_search_node(
    state: PolicySearchInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> PolicySearchOutput:
    """
    title: 政策检索
    desc: 检索与该技术相关的国家/地方政策支持，包括科技计划项目、创新基金、税收优惠、人才引进、产业扶持等政策
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 从config的metadata读取LLM配置路径
    llm_cfg_path = config.get('metadata', {}).get('llm_cfg', 'config/policy_search_llm_cfg.json')
    cfg_file = os.path.join(os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects'), llm_cfg_path)
    
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get('config', {})
    sp = _cfg.get('sp', '')
    up = _cfg.get('up', '')
    
    # 序列化技术分析结果
    tech_analysis_str = json.dumps(state.tech_analysis, ensure_ascii=False, indent=2)
    
    # 使用jinja2模板渲染提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        'tech_analysis': tech_analysis_str,
        'user_type': state.user_type
    })
    
    # 初始化LLM客户端
    client = LLMClient()
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]
    
    # 调用大模型
    response = client.invoke(
        messages=messages,
        model=llm_config.get('model', 'doubao-seed-2-0-pro-260215'),
        temperature=llm_config.get('temperature', 0.7),
        max_completion_tokens=llm_config.get('max_completion_tokens', 4096)
    )
    
    # 处理响应内容
    content = response.content
    if isinstance(content, str):
        result_text = content.strip()
    else:
        result_text = str(content)
    
    # 解析JSON结果
    try:
        policy_result = json.loads(result_text)
        policy_list = policy_result.get('policies', [])
    except:
        policy_list = [
            {
                'policy_name': '科技创新政策',
                'policy_content': result_text[:500],
                'eligibility': '适用于本技术领域',
                'support_type': '综合支持'
            }
        ]
    
    return PolicySearchOutput(policy_recommendations=policy_list)
