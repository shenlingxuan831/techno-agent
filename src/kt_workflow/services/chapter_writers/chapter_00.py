"""中游章节 Writer — 第 0 部分 — 文档说明

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_00`，在流水线中的位置：

  … → kt_structure → **kt_chapter_00** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写 BP 最前面的「封面说明」：保密级别、给谁看、数据怎么标注。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 3 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 0 个），还要返回图表 JSON

你要写的具体内容：共 3 个小节（0.1～0.3），一般是规则/模板文字，不一定需要大模型。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · 0.2 要根据 submission.user_type 决定读者是政府、投资还是企业。
  · 0.3 写清楚【事实】【推断】【待验证】三种标注，后面各章都要遵守。
  · 本章篇幅短，可先用手写规则跑通，再考虑是否接 LLM。

怎么算「做完了」？
  · 跑一遍：python src/main.py -m kt --json-file payloads/payload_kt_workflow.json
  · 打开 SQLite，看本章各模块 id 的正文不再是「脚手架占位」字样
  · 字数、表格、chart 是否符合 writer_hint 和 templates.md

================================================================================
【对接接口（必须实现/遵守）】
================================================================================
基类     : kt_workflow.services.chapter_writers._base.BaseChapterWriter
契约类型 : kt_workflow.services.chapter_writer_contract
  - ChapterWriterContext  （chapter_runner 传入的上下文 dict）
  - generate_module_text(ctx) -> str   （Markdown，含 ## {ref} {title} 首行）
  - generate_module_chart(ctx) -> ModuleChartSpec | None  （needs_chart 时）

写库由 chapter_runner 统一完成（你只管返回字符串 / chart dict）：
  - artifact_type=bp_module_text, slug=模块 id
  - artifact_type=bp_module_chart, slug=同模块 id（见 config/kt_chapter_chart_spec_schema.json）

================================================================================
【输入：ChapterWriterContext 字段】
================================================================================
  run_id          : 本次运行 id
  profile         : structured_profile v3（重点 profile["analysis"]）
  extracted_text  : 可选，原文全文；仅 excerpt 不够时再读
  module          : 当前模块 BpModuleSpec（id/ref/title/writer_hint/needs_chart）
  document_title  : 文书标题

优先使用的 analysis 字段（本章）：
#   - profile.submission.user_type（阅读对象）
#   - profile.submission.project_name
#   - profile.submission.specific_requirements

辅助工具（基类提供）：
  - self.analysis_field(ctx, "summary")
  - self.submission_field(ctx, "user_type")
  - self.module_heading(ctx)
  - self.table_chart(title, columns, rows)
  - self.mermaid_chart(title, mermaid_source)
  - self.image_ref_chart(title, storage_uri, alt)
  - self.scaffold_module_text(ctx)  （正文占位）
  - self.scaffold_module_chart(ctx)  （图表占位）

================================================================================
【图表与正文如何配对（needs_chart 模块必读）】
================================================================================
  · 同一 module id 两条库记录：bp_module_text + bp_module_chart（slug 相同）
  · 先调 generate_module_text，再调 generate_module_chart（同一 ctx）
  · 本章需实现图表的模块数：0  → 见下方 _chart_* 方法
  · JSON 规范：config/kt_chapter_chart_spec_schema.json

================================================================================
【本章模块清单（slug = id，勿改）】
================================================================================
#   - bp_ch0_0_1 | ref=0.1 | chart=否 | 封面三行
#   - bp_ch0_0_2 | ref=0.2 | chart=否 | 政府/投资/企业矩阵
#   - bp_ch0_0_3 | ref=0.3 | chart=否 | 【事实】【推断】【待验证】

字数/篇幅：0.3 节 ≤200 字；其余见 writer_hint
话术模板：docs/bp_research_commercialization_templates.md §0.1～0.3
注册表  ：config/bp_transform_outline_registry.json（chapter=0）
组员指南：docs/kt_workflow_chapter_writer_guide.md

================================================================================
【实现步骤（建议）】
================================================================================
1. 打开本文件底部的 `generate_module_text`，找到 TODO。
2. 用 `if module_id == "bp_chX_..."` 区分每个小节（id 见上方模块清单）。
3. 从 ctx 取素材：self.analysis_field(ctx, "字段名") 或 self.submission_field(ctx, "字段名")。
4. 拼 Markdown：第一行用 self.module_heading(ctx)，正文按 templates.md 写。
5. 需要大模型时：在本文件或 services/ 新文件写 prompt 函数，这里只负责调用。
6. needs_chart 的小节：在 generate_module_chart 里走 _chart_{module_id} 分支。
7. 无依据的数据写【待验证】；有材料依据写【事实】；合理推论写【推断】。
8. 自测命令：python src/main.py -m kt --json-file payloads/payload_kt_workflow.json

================================================================================
【generate_module_chart 里长什么样算写对了】
================================================================================
  · return 一个 dict（ModuleChartSpec），含 schema_version / chart_type / title / spec
  · chart_type 用 table | mermaid | image_ref（不要用 placeholder 上线）
  · 表格数据与同名正文一致；无数据时表内填【待验证】
  · 不要写库；chapter_runner 会用 module["id"] 自动存 bp_module_chart

================================================================================
【generate_module_text 里长什么样算写对了】
================================================================================
  · 第一行：## {ref} {title}  （与注册表一致）
  · 正文：人类可读的 BP 段落，不是 JSON
  · 不要 return 整个 profile；只 return **当前这一个模块** 的正文
  · slug 不用你管：程序用 module["id"] 自动存库

================================================================================
"""

from __future__ import annotations

from datetime import date

from kt_workflow.services.chapter_writer_contract import ChapterWriterContext, ModuleChartSpec
from kt_workflow.services.chapter_writers._base import BaseChapterWriter


class Chapter00Writer(BaseChapterWriter):
    """chapter=0 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 0
    IMPLEMENTER_MODULE = __name__

    def generate_module_text(self, ctx: ChapterWriterContext) -> str:
        """
        【你要改的核心函数】

        chapter_runner 每处理注册表里的一个模块，就会调用一次本函数。
        ctx["module"] 就是「当前这一小节」的信息（id、标题、writer_hint 等）。
        ctx["profile"] 是上游准备好的 structured_profile（重点用 ["analysis"]）。

        现在：所有模块都走最后的 scaffold_module_text（占位）。
        你要做：用 module_id 分支，分别 return 真实 Markdown 字符串。
        """
        mod = ctx.get("module", {}) if isinstance(ctx, dict) else {}
        module_id = mod.get("id", "")
        if module_id == "bp_ch0_0_1":
            return self._write_bp_ch0_0_1(ctx)
        if module_id == "bp_ch0_0_2":
            return self._write_bp_ch0_0_2(ctx)
        if module_id == "bp_ch0_0_3":
            return self._write_bp_ch0_0_3(ctx)

        # ---- 在这里按 module_id 添加分支（写真实正文）----
        # if module_id == "bp_ch0_0_1":
        #     return self._write_bp_ch0_0_1(ctx)

        # 未实现的模块仍返回占位（方便联调；全部实现后可删）
        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext):
        """本章无 needs_chart 模块。"""
        return None

    # ------------------------------------------------------------------

    def _value_or_pending(self, value, label: str) -> str:
        if value is None:
            return f"【待验证】{label}尚未在材料中明确。"
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (list, tuple)) and value:
            return "、".join(str(item).strip() for item in value if str(item).strip())
        return f"【待验证】{label}尚未在材料中明确。"

    def _heading(self, ctx: ChapterWriterContext) -> str:
        try:
            heading = self.module_heading(ctx)
            if heading:
                return heading
        except Exception:
            pass

        module = ctx.get("module", {}) if isinstance(ctx, dict) else {}
        ref = module.get("ref", "0.x")
        title = module.get("title", "文档说明")
        return f"## {ref} {title}"

    def _submission_value(self, ctx: ChapterWriterContext, key: str):
        try:
            value = self.submission_field(ctx, key)
            if value not in (None, "", [], {}):
                return value
        except Exception:
            pass

        profile = ctx.get("profile", {}) if isinstance(ctx, dict) else {}
        submission = profile.get("submission", {}) if isinstance(profile, dict) else {}
        return submission.get(key)

    def _reader_label(self, ctx: ChapterWriterContext) -> str:
        raw_user_type = str(self._submission_value(ctx, "user_type") or "").strip()
        lowered = raw_user_type.lower()
        if "政府" in raw_user_type or "gov" in lowered:
            return "政府评审"
        if "投资" in raw_user_type or "invest" in lowered or "fund" in lowered:
            return "投资机构"
        if "企业" in raw_user_type or "enterprise" in lowered or "company" in lowered:
            return "合作企业"
        return raw_user_type or "【待验证】阅读对象需由项目方确认"

    def _write_bp_ch0_0_1(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        project_name = self._value_or_pending(self._submission_value(ctx, "project_name"), "项目名称")
        confidentiality = self._submission_value(ctx, "confidentiality_level") or "内部"
        version = self._submission_value(ctx, "version") or "V1.0.0"
        updated_at = self._submission_value(ctx, "updated_at") or date.today().isoformat()

        return (
            f"{heading}\n\n"
            f"- **项目名称**：{project_name}\n"
            f"- **保密级别**：【推断】{confidentiality}。如涉及未公开专利、商业合同或融资材料，需由项目方确认访问权限。\n"
            f"- **版本号**：【事实】{version}\n"
            f"- **更新日期**：【事实】{updated_at}\n"
        )

    def _write_bp_ch0_0_2(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        reader = self._reader_label(ctx)

        return (
            f"{heading}\n\n"
            f"【事实】本版 BP 的主要阅读对象识别为：**{reader}**。\n\n"
            "| 章节 | 政府评审 | 投资机构 | 合作企业 |\n"
            "|------|----------|----------|----------|\n"
            "| 0. 文档说明 | 必选 | 必选 | 必选 |\n"
            "| 1. 执行摘要 | 必选 | 必选 | 必选 |\n"
            "| 2. 项目背景 | 必选 | 可选 | 可选 |\n"
            "| 3. 核心技术 | 必选 | 必选 | 必选 |\n"
            "| 4. 市场分析 | 可选 | 必选 | 可选 |\n"
            "| 5. 商业化方案 | 可选 | 必选 | 必选 |\n"
            "| 6. 团队与组织 | 必选 | 必选 | 必选 |\n"
            "| 7. 财务规划 | 可选 | 必选 | 可选 |\n"
            "| 8. 风险分析 | 必选 | 必选 | 可选 |\n"
            "| 9. 结论展望 | 必选 | 必选 | 可选 |\n"
            "| 10. 附录 | 可选 | 可选 | 可选 |\n\n"
            "【推断】必选章节应完整生成；可选章节是否纳入，应结合用户补充要求、材料完整度与最终交付场景确认。\n"
        )

    def _write_bp_ch0_0_3(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        requirements = self._value_or_pending(self._submission_value(ctx, "specific_requirements"), "用户补充要求")

        return (
            f"{heading}\n\n"
            "本 BP 后续章节统一采用以下数据标注规则：\n\n"
            "- **【事实】**：用户材料、实验数据、专利文件、第三方报告或其他可追溯来源中明确出现的信息。\n"
            "- **【推断】**：基于已提供材料进行的合理商业判断、场景归纳或路径建议。\n"
            "- **【待验证】**：材料不足、缺少来源或需要项目方进一步确认的信息。\n\n"
            "来源优先级为：内部实测数据 > 第三方报告 > 学术文献 > 行业估算。凡涉及市场规模、融资金额、客户名称、专利号和财务预测，若材料未明确提供，不得编造，必须标记为【待验证】。\n\n"
            f"用户补充要求：{requirements}\n"
        )
    # 正文私有方法示例（每个模块一个）：
    #
    # def _write_bp_ch0_0_1(self, ctx: ChapterWriterContext) -> str:
    #     """写 保密级别、版本号与更新日期 小节。"""
    #     heading = self.module_heading(ctx)
    #     summary = self.analysis_field(ctx, "summary")
    #     return f"{heading}\n\n{summary}\n"
    #
    # 图表私有方法见上方 _chart_* （与 needs_chart 模块一一对应）
    # ------------------------------------------------------------------
