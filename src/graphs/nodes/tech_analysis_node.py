"""
技术分析节点
使用大语言模型分析技术文档，评估技术成熟度、创新性、应用场景等
"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import TechAnalysisInput, TechAnalysisOutput


def _as_str_list(val) -> list:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    if isinstance(val, str) and val.strip():
        return [val.strip()]
    return []


def tech_analysis_node(
    state: TechAnalysisInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> TechAnalysisOutput:
    """
    title: 技术分析
    desc: 使用AI大模型深度分析技术文档，评估技术成熟度、创新性、技术优势与劣势、应用场景、知识产权状态等
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 从config的metadata读取LLM配置路径
    llm_cfg_path = config.get('metadata', {}).get('llm_cfg', 'config/tech_analysis_llm_cfg.json')
    cfg_file = os.path.join(os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects'), llm_cfg_path)
    
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get('config', {})
    sp = _cfg.get('sp', '')
    up = _cfg.get('up', '')
    
    # 使用jinja2模板渲染提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        'tech_text': state.tech_text[:8000],  # 限制文本长度
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
        analysis_result = json.loads(result_text)
    except:
        # 如果不是有效JSON，包装成dict
        analysis_result = {
            'raw_analysis': result_text,
            'summary': result_text[:500]
        }
    
    downstream_focus = _as_str_list(analysis_result.get("downstream_focus"))
    retrieval_queries = _as_str_list(analysis_result.get("retrieval_queries"))

    return TechAnalysisOutput(
        tech_analysis=analysis_result,
        tech_maturity=analysis_result.get('tech_maturity', '待评估'),
        tech_innovation=analysis_result.get('tech_innovation', '待评估'),
        downstream_focus=downstream_focus,
        retrieval_queries=retrieval_queries,
    )
