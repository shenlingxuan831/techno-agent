"""简版 BP 工作流：提取 → 按目录生成 Markdown → 落盘。"""

from langgraph.graph import StateGraph, END

from graphs.bp_simple.state import BPWorkflowInput, BPWorkflowOutput, BPWorkflowState
from graphs.bp_simple.nodes.extract_node import bp_simple_extract_node
from graphs.bp_simple.nodes.compose_node import bp_simple_compose_node

builder = StateGraph(BPWorkflowState, input_schema=BPWorkflowInput, output_schema=BPWorkflowOutput)

builder.add_node("bp_simple_extract", bp_simple_extract_node)
builder.add_node("bp_simple_compose", bp_simple_compose_node, metadata={
    "type": "agent",
    "llm_cfg": "config/bp_simple_llm_cfg.json",
})

builder.set_entry_point("bp_simple_extract")
builder.add_edge("bp_simple_extract", "bp_simple_compose")
builder.add_edge("bp_simple_compose", END)

bp_simple_graph = builder.compile()
