"""简版 BP：文档提取（复用主图提取逻辑）。"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.nodes.tech_doc_extract_node import tech_doc_extract_node
from graphs.state import TechDocExtractInput, TechDocExtractOutput
from graphs.bp_simple.state import BPWorkflowState


def bp_simple_extract_node(
    state: BPWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> TechDocExtractOutput:
    return tech_doc_extract_node(
        TechDocExtractInput(tech_document=state.tech_document),
        config,
        runtime,
    )
