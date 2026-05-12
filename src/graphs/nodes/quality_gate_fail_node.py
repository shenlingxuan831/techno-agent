"""
质量门失败：补齐最小分析字段，直接进入报告汇总，跳过后续 Agent。
"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import QualityGateFailInput, QualityGateFailOutput


def quality_gate_fail_node(
    state: QualityGateFailInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> QualityGateFailOutput:
    """
    title: 质量门失败汇总
    desc: 在文档未达最低要求时生成可读的占位分析结果并进入报告节点
    """
    plan = state.workflow_plan or {}
    qg = plan.get("quality_gate") or {}
    reason = qg.get("reason") or "未通过文档质量门"

    return QualityGateFailOutput(
        tech_analysis={
            "summary": "未执行技术分析：文档未通过质量门",
            "quality_gate": reason,
        },
        commercial_potential={
            "summary": "未执行商业化评估：上游质量门未通过",
        },
        error_message=reason,
    )
