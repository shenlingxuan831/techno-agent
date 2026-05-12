"""
商业化评估完成后的规划节点：生成 enabled_tracks 与可读 workflow_plan。
"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.planning import build_enabled_tracks
from graphs.state import WorkflowPlanInput, WorkflowPlanOutput


def workflow_plan_node(
    state: WorkflowPlanInput,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> WorkflowPlanOutput:
    """
    title: 并行阶段规划
    desc: 按用户类型、请求中的 workflow_tracks 及模型输出的下游重点裁剪并行分支
    """
    prev_plan = dict(state.workflow_plan or {})
    tracks, reasons = build_enabled_tracks(
        user_type=state.user_type,
        workflow_tracks=state.workflow_tracks,
        downstream_focus=state.downstream_focus,
        commercial_next_steps=state.commercial_next_steps,
    )

    prev_plan["parallel_stage"] = {
        "enabled_tracks": tracks,
        "reasons": reasons,
    }
    prev_plan.setdefault("quality_gate", {})

    return WorkflowPlanOutput(workflow_plan=prev_plan, enabled_tracks=tracks)
