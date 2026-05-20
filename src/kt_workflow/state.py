"""LangGraph state for kt_workflow: thin pointers; persisted truth lives in DB."""

from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field


class KTWorkflowInput(BaseModel):
    """HTTP/CLI 入参：与旧 GraphInput 字段对齐便于以后合并。"""

    project_name: str = Field(default="未命名项目", description="项目/案件显示名")
    source_uri: str = Field(
        default="",
        description="成果材料路径（相对仓库根或绝对路径）或 URL 占位",
    )
    user_type: str = Field(default="高校", description="读者类型，下游节点可选用")
    contact_info: str = Field(default="", description="联系方式")
    specific_requirements: str = Field(default="", description="补充说明")
    project_id: str = Field(
        default="",
        description="可选；由 GraphService.run_kt_workflow 注入，须与 SQLite 文件名所用 run 一致",
    )
    run_id: str = Field(
        default="",
        description="可选；由 Context / HTTP x-run-id 注入，与 databases/<run_id>.sqlite 一致",
    )


class KTWorkflowState(KTWorkflowInput):
    """图中传递的最小状态；各节点通过 run_id 读写的实际内容在 kt_artifacts。"""

    current_stage: str = Field(default="", description="当前阶段名，便于日志")
    errors: List[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict, description="终端输出摘要，由收尾节点填充")


class KTWorkflowOutput(BaseModel):
    project_id: str
    run_id: str
    current_stage: str
    summary: dict[str, Any] = Field(default_factory=dict)
