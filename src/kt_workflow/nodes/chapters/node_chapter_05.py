"""章 5：商业化落地方案。

图节点 kt_chapter_05 → chapter_runner(chapter=5) → Chapter05Writer
组员实现文件：kt_workflow/services/chapter_writers/chapter_05.py（本节点一般无需修改）
"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow.nodes.chapters.chapter_runner import kt_chapter_runner
from kt_workflow.state import KTWorkflowState


def kt_chapter_05_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    return kt_chapter_runner(state, config, runtime, chapter=5)
