"""
科技成果转化智能体工作流 - 主图编排
定义工作流的整体结构和节点编排
"""

from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)
from graphs.nodes.tech_doc_extract_node import tech_doc_extract_node
from graphs.nodes.tech_analysis_node import tech_analysis_node
from graphs.nodes.commercial_eval_node import commercial_eval_node
from graphs.nodes.match_requirements_node import match_requirements_node
from graphs.nodes.policy_search_node import policy_search_node
from graphs.nodes.capital_match_node import capital_match_node
from graphs.nodes.bp_generation_node import bp_generation_node
from graphs.nodes.report_generate_node import report_generate_node


# 创建状态图，指定输入输出schema
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
# 1. 技术文档提取节点（Task节点）
builder.add_node("tech_doc_extract", tech_doc_extract_node)

# 2. 技术分析节点（Agent节点）
builder.add_node("tech_analysis", tech_analysis_node, metadata={
    "type": "agent",
    "llm_cfg": "config/tech_analysis_llm_cfg.json"
})

# 3. 商业化评估节点（Agent节点）
builder.add_node("commercial_eval", commercial_eval_node, metadata={
    "type": "agent",
    "llm_cfg": "config/commercial_eval_llm_cfg.json"
})

# 4. 需求匹配节点（Agent节点）
builder.add_node("match_requirements", match_requirements_node, metadata={
    "type": "agent",
    "llm_cfg": "config/match_requirements_llm_cfg.json"
})

# 5. 政策检索节点（Agent节点）
builder.add_node("policy_search", policy_search_node, metadata={
    "type": "agent",
    "llm_cfg": "config/policy_search_llm_cfg.json"
})

# 6. 资本对接节点（Agent节点）
builder.add_node("capital_match", capital_match_node, metadata={
    "type": "agent",
    "llm_cfg": "config/capital_match_llm_cfg.json"
})

# 7. BP生成节点（Agent节点）
builder.add_node("bp_generation", bp_generation_node, metadata={
    "type": "agent",
    "llm_cfg": "config/bp_generation_llm_cfg.json"
})

# 8. 报告生成节点（Task节点）
builder.add_node("report_generate", report_generate_node)


# 设置入口点
builder.set_entry_point("tech_doc_extract")

# 添加边 - 线性流程
builder.add_edge("tech_doc_extract", "tech_analysis")
builder.add_edge("tech_analysis", "commercial_eval")

# 并行执行匹配、政策、资本对接
# 这三个节点可以同时执行
builder.add_edge("commercial_eval", "match_requirements")
builder.add_edge("commercial_eval", "policy_search")
builder.add_edge("commercial_eval", "capital_match")

# BP生成可以与其他并行任务同时进行
builder.add_edge("commercial_eval", "bp_generation")

# 汇聚到报告生成节点 - 使用列表形式添加并行分支
builder.add_edge(["match_requirements", "policy_search", "capital_match", "bp_generation"], "report_generate")

# 报告生成后结束
builder.add_edge("report_generate", END)

# 编译图
main_graph = builder.compile()
