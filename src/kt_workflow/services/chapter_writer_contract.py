"""中游章节生成共用接口类型（实现由各章 service 完成，chapter_runner 统一调用）。

文档：`docs/kt_workflow_chapter_writer_guide.md`
"""

from __future__ import annotations

from typing import Any, Protocol, TypedDict

from kt_workflow.outline_loader import BpModuleSpec


CHART_SPEC_VERSION = 1


class StructuredProfile(TypedDict, total=False):
    schema_version: int
    source: dict[str, Any]
    submission: dict[str, Any]
    content: dict[str, Any]
    analysis: dict[str, Any]
    downstream: dict[str, Any]


class ChapterWriterContext(TypedDict, total=False):
    """传给 generate_module_text 的上下文。"""

    run_id: str
    profile: StructuredProfile
    extracted_text: str | None
    module: BpModuleSpec
    document_title: str


class ModuleChartSpec(TypedDict, total=False):
    schema_version: int
    chart_type: str  # table | mermaid | image_ref | placeholder
    title: str
    spec: dict[str, Any]
    evidence_tags: list[str]


class ChapterModuleWriter(Protocol):
    def generate_module_text(self, ctx: ChapterWriterContext) -> str:
        """返回该模块 Markdown 正文（含 ## 标题行，见文档）。"""
        ...

    def generate_module_chart(self, ctx: ChapterWriterContext) -> ModuleChartSpec | None:
        """needs_chart=true 时返回图表 spec；否则 None。"""
        ...
