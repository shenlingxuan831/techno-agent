"""
资本对接节点
根据技术分析和商业化评估，推荐合适的投资机构、基金、产业资本等
"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context
from graphs.planning import should_skip_track
from graphs.state import CapitalMatchInput, CapitalMatchOutput

_TRACK_ID = "capital_match"


def capital_match_node(
    state: CapitalMatchInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CapitalMatchOutput:
    """
    title: 资本对接
    desc: 根据技术分析和商业化评估，推荐合适的投资机构、基金、产业资本等，打通技术与资本的对接渠道
    integrations: 大语言模型
    """
    ctx = runtime.context

    if should_skip_track(state.enabled_tracks, _TRACK_ID):
        return CapitalMatchOutput(capital_recommendations=[])

    # 从config的metadata读取LLM配置路径
    llm_cfg_path = config.get('metadata', {}).get('llm_cfg', 'config/capital_match_llm_cfg.json')
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
        'commercial_potential': commercial_str
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
        capital_result = json.loads(result_text)
        capital_list = capital_result.get('capital_sources', [])
    except:
        capital_list = [
            {
                'investor_name': '科技创新基金',
                'investment_stage': '早中期',
                'investment_fields': '科技创新',
                'match_score': 0.8,
                'contact_info': result_text[:200]
            }
        ]
    
    return CapitalMatchOutput(capital_recommendations=capital_list)
