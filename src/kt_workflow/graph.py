"""LangGraph：ingest → extract → analyze → structure → 按章 0..10 顺序写库 → aggregate → polish → pdf。"""

from langgraph.graph import END, StateGraph

from kt_workflow.nodes.chapters.node_chapter_00 import kt_chapter_00_node
from kt_workflow.nodes.chapters.node_chapter_01 import kt_chapter_01_node
from kt_workflow.nodes.chapters.node_chapter_02 import kt_chapter_02_node
from kt_workflow.nodes.chapters.node_chapter_03 import kt_chapter_03_node
from kt_workflow.nodes.chapters.node_chapter_04 import kt_chapter_04_node
from kt_workflow.nodes.chapters.node_chapter_05 import kt_chapter_05_node
from kt_workflow.nodes.chapters.node_chapter_06 import kt_chapter_06_node
from kt_workflow.nodes.chapters.node_chapter_07 import kt_chapter_07_node
from kt_workflow.nodes.chapters.node_chapter_08 import kt_chapter_08_node
from kt_workflow.nodes.chapters.node_chapter_09 import kt_chapter_09_node
from kt_workflow.nodes.chapters.node_chapter_10 import kt_chapter_10_node
from kt_workflow.nodes.node_aggregate import kt_aggregate_node
from kt_workflow.nodes.node_analyze import kt_analyze_node
from kt_workflow.nodes.node_extract import kt_extract_node
from kt_workflow.nodes.node_ingest import kt_ingest_node
from kt_workflow.nodes.node_pdf_export import kt_pdf_export_node
from kt_workflow.nodes.node_polish import kt_polish_node
from kt_workflow.nodes.node_structure import kt_structure_node
from kt_workflow.state import KTWorkflowInput, KTWorkflowOutput, KTWorkflowState

builder = StateGraph(
    KTWorkflowState,
    input_schema=KTWorkflowInput,
    output_schema=KTWorkflowOutput,
)

builder.add_node("kt_ingest", kt_ingest_node)
builder.add_node("kt_extract", kt_extract_node)
builder.add_node("kt_analyze", kt_analyze_node)
builder.add_node("kt_structure", kt_structure_node)
builder.add_node("kt_chapter_00", kt_chapter_00_node)
builder.add_node("kt_chapter_01", kt_chapter_01_node)
builder.add_node("kt_chapter_02", kt_chapter_02_node)
builder.add_node("kt_chapter_03", kt_chapter_03_node)
builder.add_node("kt_chapter_04", kt_chapter_04_node)
builder.add_node("kt_chapter_05", kt_chapter_05_node)
builder.add_node("kt_chapter_06", kt_chapter_06_node)
builder.add_node("kt_chapter_07", kt_chapter_07_node)
builder.add_node("kt_chapter_08", kt_chapter_08_node)
builder.add_node("kt_chapter_09", kt_chapter_09_node)
builder.add_node("kt_chapter_10", kt_chapter_10_node)
builder.add_node("kt_aggregate", kt_aggregate_node)
builder.add_node("kt_polish", kt_polish_node)
builder.add_node("kt_pdf", kt_pdf_export_node)

builder.set_entry_point("kt_ingest")
builder.add_edge("kt_ingest", "kt_extract")
builder.add_edge("kt_extract", "kt_analyze")
builder.add_edge("kt_analyze", "kt_structure")
builder.add_edge("kt_structure", "kt_chapter_00")
builder.add_edge("kt_chapter_00", "kt_chapter_01")
builder.add_edge("kt_chapter_01", "kt_chapter_02")
builder.add_edge("kt_chapter_02", "kt_chapter_03")
builder.add_edge("kt_chapter_03", "kt_chapter_04")
builder.add_edge("kt_chapter_04", "kt_chapter_05")
builder.add_edge("kt_chapter_05", "kt_chapter_06")
builder.add_edge("kt_chapter_06", "kt_chapter_07")
builder.add_edge("kt_chapter_07", "kt_chapter_08")
builder.add_edge("kt_chapter_08", "kt_chapter_09")
builder.add_edge("kt_chapter_09", "kt_chapter_10")
builder.add_edge("kt_chapter_10", "kt_aggregate")
builder.add_edge("kt_aggregate", "kt_polish")
builder.add_edge("kt_polish", "kt_pdf")
builder.add_edge("kt_pdf", END)

kt_workflow_graph = builder.compile()
