"""
技术文档质量门：提取后校验文本长度，未通过则后续走失败短路。
"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import QualityGateInput, QualityGateOutput


def quality_gate_node(
    state: QualityGateInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> QualityGateOutput:
    """
    title: 文档质量门
    desc: 根据提取文本长度做最小质量校验，避免无效文档进入大模型分析
    """
    text = (state.tech_text or "").strip()
    threshold = state.min_tech_text_chars
    ok = len(text) >= threshold
    reason = ""
    if not ok:
        reason = f"提取文本过短（{len(text)} 字符 < 阈值 {threshold}），请检查文档或路径"

    qg = {
        "passed": ok,
        "reason": reason,
        "tech_text_len": len(text),
        "threshold": threshold,
    }
    return QualityGateOutput(workflow_plan={"quality_gate": qg})
