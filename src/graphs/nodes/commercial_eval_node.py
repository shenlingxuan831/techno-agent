"""
商业化潜力评估节点
基于技术分析结果，评估技术的市场潜力、竞争优势、商业化路径等
"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import CommercialEvalInput, CommercialEvalOutput


def _as_str_list(val) -> list:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    if isinstance(val, str) and val.strip():
        return [val.strip()]
    return []


def commercial_eval_node(
    state: CommercialEvalInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CommercialEvalOutput:
    """
    title: 商业化潜力评估
    desc: 基于技术分析结果，评估技术的市场潜力、竞争优势、商业化路径、风险因素等，为投资决策提供依据
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 从config的metadata读取LLM配置路径
    llm_cfg_path = config.get('metadata', {}).get('llm_cfg', 'config/commercial_eval_llm_cfg.json')
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
        eval_result = json.loads(result_text)
    except:
        eval_result = {
            'raw_evaluation': result_text,
            'summary': result_text[:500]
        }
    
    next_steps = _as_str_list(eval_result.get("commercial_next_steps"))
    diligence = _as_str_list(eval_result.get("due_diligence_topics"))

    return CommercialEvalOutput(
        commercial_potential=eval_result,
        market_size=eval_result.get('market_size', '待评估'),
        competitive_advantage=eval_result.get('competitive_advantage', '待评估'),
        commercial_next_steps=next_steps,
        due_diligence_topics=diligence,
    )
