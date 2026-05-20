"""章节 Writer 基类：脚手架默认实现与共用工具。

由 `chapter_runner.kt_chapter_runner` 按章调用；子类见 `chapter_00.py` … `chapter_10.py`。
"""

from __future__ import annotations

from typing import Any

from kt_workflow.services.chapter_writer_contract import (
    CHART_SPEC_VERSION,
    ChapterWriterContext,
    ModuleChartSpec,
)

# 注册表 needs_chart 模块 → 建议实现的 chart_type（组员实现时可改）
_SUGGESTED_CHART_TYPE: dict[str, str] = {
    "bp_ch2_2_4": "mermaid",
    "bp_ch3_3_1": "mermaid",
    "bp_ch3_3_3": "table",
    "bp_ch3_3_4": "table",
    "bp_ch3_3_5": "table",
    "bp_ch4_4_1": "mermaid",
    "bp_ch4_4_2": "table",
    "bp_ch4_4_3": "table",
    "bp_ch4_4_5": "table",
    "bp_ch5_5_2": "mermaid",
    "bp_ch5_5_3_1": "mermaid",
    "bp_ch5_5_4": "mermaid",
    "bp_ch5_5_5_1": "mermaid",
    "bp_ch6_6_1": "table",
    "bp_ch6_6_3": "image_ref",
    "bp_ch6_6_5": "table",
    "bp_ch7_7_1": "table",
    "bp_ch7_7_2": "table",
    "bp_ch7_7_3": "table",
    "bp_ch7_7_4": "table",
    "bp_ch8_8_5": "table",
}


class BaseChapterWriter:
    """各章 Writer 的基类。子类应设置 CHAPTER 与 IMPLEMENTER_MODULE。"""

    CHAPTER: int = -1
    IMPLEMENTER_MODULE: str = "kt_workflow.services.chapter_writers._base"

    def generate_module_text(self, ctx: ChapterWriterContext) -> str:
        """
        生成单个模块 Markdown 正文（含 ## 标题行）。

        组员实现方式（二选一）：
        1. 在本类中 override 本方法，按 `ctx["module"]["id"]` 分支；
        2. 新增 `_module_{id}(ctx)` 私有方法并在本方法内 dispatch。
        """
        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext) -> ModuleChartSpec | None:
        """needs_chart=true 时由 chapter_runner 调用；子类按 module_id 分支或返回 scaffold。"""
        mod = ctx["module"]
        if not mod.get("needs_chart"):
            return None
        return self.scaffold_module_chart(ctx)

    # ------------------------------------------------------------------ helpers

    def scaffold_module_chart(self, ctx: ChapterWriterContext) -> ModuleChartSpec:
        """开发阶段图表占位：标明 module id、建议 chart_type、writer_hint。"""
        mod = ctx["module"]
        mid = mod.get("id", "")
        ref = str(mod.get("ref", ""))
        title = str(mod.get("title", "图表"))
        hint = str(mod.get("writer_hint") or "")
        suggested = _SUGGESTED_CHART_TYPE.get(mid, "table")
        return {
            "schema_version": CHART_SPEC_VERSION,
            "chart_type": "placeholder",
            "title": title,
            "spec": {
                "module_id": mid,
                "ref": ref,
                "status": "scaffold",
                "suggested_chart_type": suggested,
                "writer_hint": hint,
                "implement_in": self.IMPLEMENTER_MODULE,
                "note": (
                    f"请在 {self.IMPLEMENTER_MODULE} 中实现 _chart_{mid}(ctx)，"
                    f"或在本类 generate_module_chart 分支里返回 table/mermaid/image_ref。"
                    f"规范见 config/kt_chapter_chart_spec_schema.json"
                ),
            },
        }

    def scaffold_module_text(self, ctx: ChapterWriterContext) -> str:
        """开发阶段占位正文：标明模块 id、hint、可用 analysis 字段摘要。"""
        mod = ctx["module"]
        ref = mod.get("ref", "")
        title = mod.get("title", "")
        mid = mod.get("id", "")
        hint = mod.get("writer_hint", "")
        doc_title = ctx.get("document_title", "BP")
        analysis = (ctx.get("profile") or {}).get("analysis") or {}
        summary = str(analysis.get("summary") or "")[:120]
        tech = str(analysis.get("tech_name") or "待验证")
        trl = str(analysis.get("trl_level") or ctx.get("profile", {}).get("content", {}).get("trl_hint") or "待验证")

        hint_block = f"\n\n> **写作提示**：{hint}\n" if hint else ""
        return (
            f"## {ref} {title}\n\n"
            f"**状态**：脚手架占位（待 `{self.IMPLEMENTER_MODULE}` 实现真实生成）\n\n"
            f"- **模块 id（写库 slug）**：`{mid}`\n"
            f"- **所属文书**：{doc_title}\n"
            f"- **上游摘要**：{tech}；TRL {trl}\n"
            f"- **analysis.summary 摘录**：{summary or '（空）'}…\n"
            f"{hint_block}\n"
            f"请在本文件实现 `generate_module_text`，并遵守 "
            f"`docs/kt_workflow_chapter_writer_guide.md` 中的证据标注 "
            f"【事实】/【推断】/【待验证】。\n"
        )

    @staticmethod
    def analysis_field(ctx: ChapterWriterContext, key: str, default: str = "") -> str:
        analysis = (ctx.get("profile") or {}).get("analysis") or {}
        val = analysis.get(key, default)
        if val is None:
            return default
        if isinstance(val, list):
            return "；".join(str(x) for x in val if str(x).strip()) or default
        return str(val) if str(val).strip() else default

    @staticmethod
    def submission_field(ctx: ChapterWriterContext, key: str, default: str = "") -> str:
        sub = (ctx.get("profile") or {}).get("submission") or {}
        val = sub.get(key, default)
        return str(val) if val is not None and str(val).strip() else default

    @staticmethod
    def module_heading(ctx: ChapterWriterContext) -> str:
        mod = ctx["module"]
        return f"## {mod.get('ref', '')} {mod.get('title', '')}"

    @staticmethod
    def table_chart(title: str, columns: list[str], rows: list[list[str]]) -> ModuleChartSpec:
        return {
            "schema_version": CHART_SPEC_VERSION,
            "chart_type": "table",
            "title": title,
            "spec": {"columns": columns, "rows": rows},
        }

    @staticmethod
    def mermaid_chart(title: str, source: str, diagram_type: str = "flowchart") -> ModuleChartSpec:
        return {
            "schema_version": CHART_SPEC_VERSION,
            "chart_type": "mermaid",
            "title": title,
            "spec": {"diagram_type": diagram_type, "source": source},
        }

    @staticmethod
    def image_ref_chart(title: str, storage_uri: str, alt: str = "") -> ModuleChartSpec:
        return {
            "schema_version": CHART_SPEC_VERSION,
            "chart_type": "image_ref",
            "title": title,
            "spec": {"storage_uri": storage_uri, "alt": alt or title},
        }
