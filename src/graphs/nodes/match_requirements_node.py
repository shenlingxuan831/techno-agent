"""
需求匹配节点
根据技术分析结果，匹配相关的企业需求、技术需求、产业需求
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
from graphs.state import MatchRequirementsInput, MatchRequirementsOutput

_TRACK_ID = "match_requirements"


def match_requirements_node(
    state: MatchRequirementsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> MatchRequirementsOutput:
    """
    title: 需求匹配
    desc: 根据技术分析结果，智能匹配相关的企业需求、技术需求、产业需求，打通技术供给与市场需求的对接
    integrations: 大语言模型
    """
    ctx = runtime.context

    if should_skip_track(state.enabled_tracks, _TRACK_ID):
        return MatchRequirementsOutput(matched_requirements=[])

    # 从config的metadata读取LLM配置路径
    llm_cfg_path = config.get('metadata', {}).get('llm_cfg', 'config/match_requirements_llm_cfg.json')
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
        match_result = json.loads(result_text)
        matched_list = match_result.get('matched_requirements', [])
    except:
        matched_list = [
            {
                'requirement': result_text[:500],
                'match_score': 0.0,
                'source': '分析生成'
            }
        ]
    
    return MatchRequirementsOutput(matched_requirements=matched_list)
