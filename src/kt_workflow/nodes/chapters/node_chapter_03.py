"""章 3：核心技术与科研成果。

图节点 kt_chapter_03 → chapter_runner(chapter=3) → Chapter03Writer
组员实现文件：kt_workflow/services/chapter_writers/chapter_03.py（本节点一般无需修改）
"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from coze_coding_utils.runtime_ctx.context import Context

from kt_workflow.nodes.chapters.chapter_runner import kt_chapter_runner
from kt_workflow.state import KTWorkflowState


def kt_chapter_03_node(
    state: KTWorkflowState,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> dict:
    return kt_chapter_runner(state, config, runtime, chapter=3)
