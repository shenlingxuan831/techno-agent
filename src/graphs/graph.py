"""
科技成果转化智能体工作流 - 主图编排
定义工作流的整体结构和节点编排（含质量门与可配置并行规划）
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import StateGraph, END
from graphs.state import GlobalState, GraphInput, GraphOutput
from graphs.nodes.tech_doc_extract_node import tech_doc_extract_node
from graphs.nodes.quality_gate_node import quality_gate_node
from graphs.nodes.quality_gate_fail_node import quality_gate_fail_node
from graphs.nodes.tech_analysis_node import tech_analysis_node
from graphs.nodes.commercial_eval_node import commercial_eval_node
from graphs.nodes.workflow_plan_node import workflow_plan_node
from graphs.nodes.match_requirements_node import match_requirements_node
from graphs.nodes.policy_search_node import policy_search_node
from graphs.nodes.capital_match_node import capital_match_node
from graphs.nodes.bp_generation_node import bp_generation_node
from graphs.nodes.report_generate_node import (
    report_generate_node,
    report_generate_degraded_node,
)


def route_after_quality_gate(state: Any) -> str:
    """质量门通过 → 技术分析；否则 → 失败短路。"""
    if isinstance(state, dict):
        plan = state.get("workflow_plan") or {}
    else:
        plan = getattr(state, "workflow_plan", None) or {}
    qg = plan.get("quality_gate") or {}
    if qg.get("passed"):
        return "tech_analysis"
    return "quality_gate_fail"


# 创建状态图，指定输入输出schema
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 文档提取与质量门
builder.add_node("tech_doc_extract", tech_doc_extract_node)
builder.add_node("quality_gate", quality_gate_node)
builder.add_node("quality_gate_fail", quality_gate_fail_node)

# Agent / Task 节点
builder.add_node("tech_analysis", tech_analysis_node, metadata={
    "type": "agent",
    "llm_cfg": "config/tech_analysis_llm_cfg.json"
})
builder.add_node("commercial_eval", commercial_eval_node, metadata={
    "type": "agent",
    "llm_cfg": "config/commercial_eval_llm_cfg.json"
})
builder.add_node("workflow_plan", workflow_plan_node)

builder.add_node("match_requirements", match_requirements_node, metadata={
    "type": "agent",
    "llm_cfg": "config/match_requirements_llm_cfg.json"
})
builder.add_node("policy_search", policy_search_node, metadata={
    "type": "agent",
    "llm_cfg": "config/policy_search_llm_cfg.json"
})
builder.add_node("capital_match", capital_match_node, metadata={
    "type": "agent",
    "llm_cfg": "config/capital_match_llm_cfg.json"
})
builder.add_node("bp_generation", bp_generation_node, metadata={
    "type": "agent",
    "llm_cfg": "config/bp_generation_llm_cfg.json"
})

builder.add_node("report_generate", report_generate_node)
# 与 report_generate 逻辑相同，避免与「四路汇聚屏障」冲突的独立入口
builder.add_node("report_generate_degraded", report_generate_degraded_node)

builder.set_entry_point("tech_doc_extract")

builder.add_edge("tech_doc_extract", "quality_gate")
builder.add_conditional_edges(
    "quality_gate",
    route_after_quality_gate,
    {
        "tech_analysis": "tech_analysis",
        "quality_gate_fail": "quality_gate_fail",
    },
)

builder.add_edge("tech_analysis", "commercial_eval")
builder.add_edge("commercial_eval", "workflow_plan")

# 规划后仍进入全部并行节点；未启用的分支在节点内立即返回空结果（屏障仍可达）
builder.add_edge("workflow_plan", "match_requirements")
builder.add_edge("workflow_plan", "policy_search")
builder.add_edge("workflow_plan", "capital_match")
builder.add_edge("workflow_plan", "bp_generation")

builder.add_edge(
    ["match_requirements", "policy_search", "capital_match", "bp_generation"],
    "report_generate",
)
builder.add_edge("report_generate", END)

builder.add_edge("quality_gate_fail", "report_generate_degraded")
builder.add_edge("report_generate_degraded", END)

main_graph = builder.compile()
