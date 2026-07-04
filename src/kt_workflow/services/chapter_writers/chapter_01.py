"""中游章节 Writer — 第一章 — 执行摘要

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_01`，在流水线中的位置：

  … → kt_structure → **kt_chapter_01** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写「执行摘要」：整份 BP 的电梯演讲，拆成 6 个小块分别生成。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 6 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 0 个），还要返回图表 JSON

你要写的具体内容：6 个模块（1.1～1.6）各写一段；合起来 800～1200 字，注意别写太长。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · 素材主要在 profile.analysis：summary、target_market、advantages 等。
  · 1.5 财务材料里往往没有 → 写【待验证】，不要编融资额。
  · 1.1 一句话介绍尽量 ≤50 字，用 tech_name + 场景话术。

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
#   - profile.analysis.summary
#   - profile.analysis.tech_name
#   - profile.analysis.target_market
#   - profile.analysis.advantages
#   - profile.analysis.competitive_landscape
#   - profile.analysis.application_scenarios
#   - profile.analysis.disadvantages
#   - profile.analysis.data_gaps

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
#   - bp_ch1_1_1 | ref=1.1 | chart=否 | ≤50 字话术
#   - bp_ch1_1_2 | ref=1.2 | chart=否 | TAM/SAM/SOM
#   - bp_ch1_1_3 | ref=1.3 | chart=否 | ≤3 点
#   - bp_ch1_1_4 | ref=1.4 | chart=否 | 盈利/定价/渠道
#   - bp_ch1_1_5 | ref=1.5 | chart=否 | 缺则【待验证】
#   - bp_ch1_1_6 | ref=1.6 | chart=否 | 可行/谨慎/不可行

字数/篇幅：整章合计 800～1200 字（六块拆分）
话术模板：templates.md §一、执行摘要
注册表  ：config/bp_transform_outline_registry.json（chapter=1）
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

from kt_workflow.services.chapter_writer_contract import ChapterWriterContext, ModuleChartSpec
from kt_workflow.services.chapter_writers._base import BaseChapterWriter


class Chapter01Writer(BaseChapterWriter):
    """chapter=1 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 1
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
        if module_id == "bp_ch1_1_1":
            return self._write_bp_ch1_1_1(ctx)
        if module_id == "bp_ch1_1_2":
            return self._write_bp_ch1_1_2(ctx)
        if module_id == "bp_ch1_1_3":
            return self._write_bp_ch1_1_3(ctx)
        if module_id == "bp_ch1_1_4":
            return self._write_bp_ch1_1_4(ctx)
        if module_id == "bp_ch1_1_5":
            return self._write_bp_ch1_1_5(ctx)
        if module_id == "bp_ch1_1_6":
            return self._write_bp_ch1_1_6(ctx)

        # ---- 在这里按 module_id 添加分支（写真实正文）----
        # if module_id == "bp_ch1_1_1":
        #     return self._write_bp_ch1_1_1(ctx)

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
        ref = module.get("ref", "1.x")
        title = module.get("title", "执行摘要")
        return f"## {ref} {title}"

    def _analysis_value(self, ctx: ChapterWriterContext, key: str):
        try:
            value = self.analysis_field(ctx, key)
            if value not in (None, "", [], {}):
                return value
        except Exception:
            pass

        profile = ctx.get("profile", {}) if isinstance(ctx, dict) else {}
        analysis = profile.get("analysis", {}) if isinstance(profile, dict) else {}
        return analysis.get(key)

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

    def _as_list(self, value) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, tuple):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def _bullet_points(self, values: list[str], max_items: int = 3) -> str:
        if not values:
            return "- 【待验证】材料中尚未提供足够信息。\n"
        return "".join(f"- 【事实】{item}\n" for item in values[:max_items])

    def _write_bp_ch1_1_1(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self._heading(ctx),
            section_brief="执行摘要-一句话介绍：成果名称、目标用户/场景、核心价值，避免重复长句。",
            word_limit=130,
            fallback=lambda: self._legacy_write_bp_ch1_1_1(ctx),
        )

    def _write_bp_ch1_1_2(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self._heading(ctx),
            section_brief="执行摘要-市场与场景：目标市场、应用场景；无依据不写 TAM/CAGR 数字，列出 data_gaps。",
            word_limit=220,
            fallback=lambda: self._legacy_write_bp_ch1_1_2(ctx),
        )

    def _write_bp_ch1_1_3(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self._heading(ctx),
            section_brief="执行摘要-竞争优势：优势要点与竞争格局，缺量化对比则标【待验证】。",
            word_limit=220,
            fallback=lambda: self._legacy_write_bp_ch1_1_3(ctx),
        )

    def _write_bp_ch1_1_4(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self._heading(ctx),
            section_brief="执行摘要-商业模式：可行商业化路径（交付/授权/合作），不写具体定价数字。",
            word_limit=200,
            fallback=lambda: self._legacy_write_bp_ch1_1_4(ctx),
        )

    def _write_bp_ch1_1_5(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self._heading(ctx),
            section_brief="执行摘要-财务要点：仅说明测算框架与 data_gaps，禁止编造融资额/收入。",
            word_limit=200,
            fallback=lambda: self._legacy_write_bp_ch1_1_5(ctx),
        )

    def _write_bp_ch1_1_6(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self._heading(ctx),
            section_brief="执行摘要-风险与结论：关键风险、阶段性推进结论（谨慎/可行），引用 disadvantages 与 data_gaps。",
            word_limit=200,
            fallback=lambda: self._legacy_write_bp_ch1_1_6(ctx),
        )

    def _legacy_write_bp_ch1_1_1(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        tech_name = self._analysis_value(ctx, "tech_name") or self._submission_value(ctx, "project_name")
        scenarios = self._as_list(self._analysis_value(ctx, "application_scenarios"))
        target_market = self._analysis_value(ctx, "target_market")

        if tech_name and scenarios:
            sentence = f"【推断】{tech_name}面向{scenarios[0]}场景，提供科研成果商业化解决方案。"
        elif tech_name and target_market:
            sentence = f"【推断】{tech_name}面向{target_market}市场，提供科研成果商业化解决方案。"
        else:
            sentence = "【待验证】成果名称、核心技术或应用场景仍需补充，暂无法形成完整一句话介绍。"

        return f"{heading}\n\n{sentence}\n"

    def _legacy_write_bp_ch1_1_2(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        target_market = self._value_or_pending(self._analysis_value(ctx, "target_market"), "目标市场")
        scenarios = self._value_or_pending(self._analysis_value(ctx, "application_scenarios"), "应用场景")
        gaps = self._value_or_pending(self._analysis_value(ctx, "data_gaps"), "市场规模、CAGR、TAM/SAM/SOM 数据")

        return (
            f"{heading}\n\n"
            f"【事实】目标市场：{target_market}\n\n"
            f"【事实】主要应用场景：{scenarios}\n\n"
            f"【待验证】当前执行摘要暂不编造 TAM/SAM/SOM、CAGR 或市场规模数字；需补充依据：{gaps}\n"
        )

    def _legacy_write_bp_ch1_1_3(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        advantages = self._as_list(self._analysis_value(ctx, "advantages"))
        competitive_landscape = self._analysis_value(ctx, "competitive_landscape")

        body = self._bullet_points(advantages, max_items=3)
        if competitive_landscape:
            body += f"\n【事实】竞争格局摘要：{competitive_landscape}\n"
        else:
            body += "\n【待验证】尚缺少与竞品的量化对比，后续需补充参数、成本、效率或验证数据。\n"
        return f"{heading}\n\n{body}"

    def _legacy_write_bp_ch1_1_4(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        scenarios = self._value_or_pending(self._analysis_value(ctx, "application_scenarios"), "应用场景")
        target_market = self._value_or_pending(self._analysis_value(ctx, "target_market"), "目标客户或市场")

        return (
            f"{heading}\n\n"
            f"【推断】基于当前应用场景（{scenarios}）和目标市场（{target_market}），可优先采用项目制交付、技术授权、联合开发或示范场景共建等商业化路径。\n\n"
            "【待验证】定价方式、渠道伙伴、收费周期和合同模式尚需结合客户访谈、试点成本与交付边界进一步确认。\n"
        )

    def _legacy_write_bp_ch1_1_5(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        data_gaps = self._value_or_pending(self._analysis_value(ctx, "data_gaps"), "财务测算数据")

        return (
            f"{heading}\n\n"
            "【待验证】当前材料未稳定提供本轮融资金额、资金用途、年度营收预测、毛利率、现金流和回本周期等财务要点。\n\n"
            f"【事实】需优先补充或核验的缺口：{data_gaps}\n\n"
            "【推断】在财务数据补齐前，本章只能说明测算框架，不能输出具体融资额、收入规模或回本时间。\n"
        )

    def _legacy_write_bp_ch1_1_6(self, ctx: ChapterWriterContext) -> str:
        heading = self._heading(ctx)
        risks = self._as_list(self._analysis_value(ctx, "disadvantages"))
        gaps = self._as_list(self._analysis_value(ctx, "data_gaps"))

        risk_text = risks[0] if risks else "关键商业化风险尚未在材料中充分展开"
        conclusion = "谨慎" if gaps else "可行"

        return (
            f"{heading}\n\n"
            f"【事实】当前识别的关键风险：{risk_text}。\n\n"
            "【推断】建议通过补充验证数据、明确试点客户、完善知识产权与财务测算来降低决策不确定性。\n\n"
            f"【推断】阶段性结论：**{conclusion}推进**。若后续补齐市场、财务和验证数据，可进一步提高结论置信度。\n"
        )
    # 正文私有方法示例（每个模块一个）：
    #
    # def _write_bp_ch1_1_1(self, ctx: ChapterWriterContext) -> str:
    #     """写 项目一句话介绍 小节。"""
    #     heading = self.module_heading(ctx)
    #     summary = self.analysis_field(ctx, "summary")
    #     return f"{heading}\n\n{summary}\n"
    #
    # 图表私有方法见上方 _chart_* （与 needs_chart 模块一一对应）
    # ------------------------------------------------------------------
