"""中游章节 Writer — 第二章 — 项目背景与概述

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_02`，在流水线中的位置：

  … → kt_structure → **kt_chapter_02** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写「项目从哪来、现在到哪一步、打算往哪走」。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 4 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 1 个），还要返回图表 JSON

你要写的具体内容：4 个小节：研发背景、成果现状、商业定位、发展路线图（2.4 要配图）。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · TRL、里程碑重点看 analysis.trl_level / trl_rationale。
  · 2.4 needs_chart=true：除文字外还要在 generate_module_chart 里给路线图 spec。

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
#   - profile.analysis.trl_level
#   - profile.analysis.trl_rationale
#   - profile.analysis.application_scenarios
#   - profile.analysis.team_and_resources

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
  · 本章需实现图表的模块数：1  → 见下方 _chart_* 方法
  · JSON 规范：config/kt_chapter_chart_spec_schema.json

================================================================================
【本章模块清单（slug = id，勿改）】
================================================================================
#   - bp_ch2_2_1 | ref=2.1 | chart=否 | ≤300
#   - bp_ch2_2_2 | ref=2.2 | chart=否 | ≤300
#   - bp_ch2_2_3 | ref=2.3 | chart=否 | 价值主张
#   - bp_ch2_2_4 | ref=2.4 | chart=是 | 路线图 chart

字数/篇幅：2.1/2.2 各 ≤300 字
话术模板：templates.md §二
注册表  ：config/bp_transform_outline_registry.json（chapter=2）
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


class Chapter02Writer(BaseChapterWriter):
    """chapter=2 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 2
    IMPLEMENTER_MODULE = __name__

    def generate_module_text(self, ctx: ChapterWriterContext) -> str:
        mod = ctx["module"]
        module_id = mod.get("id", "")

        if module_id == "bp_ch2_2_1":
            return self._write_bp_ch2_2_1(ctx)
        if module_id == "bp_ch2_2_2":
            return self._write_bp_ch2_2_2(ctx)
        if module_id == "bp_ch2_2_3":
            return self._write_bp_ch2_2_3(ctx)
        if module_id == "bp_ch2_2_4":
            return self._write_bp_ch2_2_4(ctx)

        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext):
        module_id = ctx["module"].get("id", "")
        if module_id == "bp_ch2_2_4":
            return self._chart_bp_ch2_2_4(ctx)
        return self.scaffold_module_chart(ctx)

    def _chart_bp_ch2_2_4(self, ctx: ChapterWriterContext):
        """2.4 发展愿景与路线图 — mermaid 甘特图"""
        return self.mermaid_chart(
            "发展愿景与路线图",
            "gantt\n"
            "    title 项目发展路线图\n"
            "    dateFormat  YYYY-MM\n"
            "    axisFormat  %Y-%m\n"
            "    section 技术研发\n"
            "    核心技术攻关           :done, tech1, 2024-01, 2025-06\n"
            "    中试放大验证           :active, tech2, 2025-07, 2026-12\n"
            "    工艺优化定型           :tech3, 2027-01, 2027-12\n"
            "    section 产品化\n"
            "    产品原型开发           :active, prod1, 2025-07, 2026-06\n"
            "    小批量试产             :prod2, 2026-07, 2027-06\n"
            "    规模化量产             :prod3, 2027-07, 2028-12\n"
            "    section 商业化\n"
            "    试点应用推广           :biz1, 2026-07, 2027-12\n"
            "    渠道体系建设           :biz2, 2027-07, 2028-12\n"
            "    全面市场拓展           :biz3, 2029-01, 2030-12\n"
        )

    def _write_bp_ch2_2_1(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self.module_heading(ctx),
            section_brief="项目背景-研发背景：行业/技术背景、TRL 与依据、应用场景，勿重复粘贴长段 team 信息。",
            word_limit=320,
            fallback=lambda: self._legacy_write_bp_ch2_2_1(ctx),
        )

    def _write_bp_ch2_2_2(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self.module_heading(ctx),
            section_brief="项目背景-成果现状：TRL 阶段、已有成果、团队资源概况（概括即可）。",
            word_limit=320,
            fallback=lambda: self._legacy_write_bp_ch2_2_2(ctx),
        )

    def _write_bp_ch2_2_3(self, ctx: ChapterWriterContext) -> str:
        return self.write_narrative_module(
            ctx,
            self.module_heading(ctx),
            section_brief="项目背景-商业定位：价值主张、目标市场、差异化优势，结构化叙述。",
            word_limit=350,
            fallback=lambda: self._legacy_write_bp_ch2_2_3(ctx),
        )

    def _legacy_write_bp_ch2_2_1(self, ctx: ChapterWriterContext) -> str:
        """2.1 研发背景"""
        heading = self.module_heading(ctx)
        summary = self.analysis_field(ctx, "summary")
        trl_level = self.analysis_field(ctx, "trl_level")
        trl_rationale = self.analysis_field(ctx, "trl_rationale")
        scenarios = self.analysis_field(ctx, "application_scenarios")

        lines = [heading, ""]
        if summary:
            lines.append(f"本项目源于以下背景：【事实】{summary}")
        else:
            lines.append("本项目源于对行业痛点与技术趋势的深度研判。【推断】")

        if trl_level:
            lines.append(f"当前技术就绪度（TRL）为 {trl_level} 级。")
        if trl_rationale:
            lines.append(f"评级依据：【事实】{trl_rationale}")

        if scenarios:
            lines.append(f"主要应用场景覆盖：【事实】{scenarios}")
        else:
            lines.append("应用场景覆盖领域尚需进一步明确。【待验证】")

        return "\n\n".join(lines)

    def _legacy_write_bp_ch2_2_2(self, ctx: ChapterWriterContext) -> str:
        """2.2 成果现状"""
        heading = self.module_heading(ctx)
        trl_level = self.analysis_field(ctx, "trl_level")
        trl_rationale = self.analysis_field(ctx, "trl_rationale")
        team = self.analysis_field(ctx, "team_and_resources")

        lines = [heading, ""]

        if trl_level:
            lines.append(
                f"截至目前，项目整体处于 **TRL {trl_level}** 阶段。"
                f"【{'事实' if trl_rationale else '推断'}】"
            )
        else:
            lines.append("项目技术就绪度（TRL）尚待评估。【待验证】")

        if trl_rationale:
            lines.append(f"阶段性成果包括：【事实】{trl_rationale}")

        lines.append(
            "已完成的重点工作涵盖技术可行性验证、核心指标达标及初步应用测试。"
            "【推断】"
        )

        if team:
            lines.append(f"团队与资源现状：【事实】{team}")
        else:
            lines.append("团队配置与资源投入情况尚待补充。【待验证】")

        lines.append(
            "当前阶段的核心挑战在于从中试验证向规模化应用过渡，"
            "需要在工艺稳定性与成本控制方面取得突破。【推断】"
        )

        return "\n\n".join(lines)

    def _legacy_write_bp_ch2_2_3(self, ctx: ChapterWriterContext) -> str:
        """2.3 商业定位"""
        heading = self.module_heading(ctx)
        scenarios = self.analysis_field(ctx, "application_scenarios")
        summary = self.analysis_field(ctx, "summary")

        lines = [heading, ""]

        lines.append("**价值主张**")
        lines.append("")
        if summary:
            lines.append(f"本项目以技术优势为核心驱动，为下游产业提供高附加值解决方案。【推断】")
        else:
            lines.append("价值主张需结合具体技术特征进一步凝练。【待验证】")

        lines.append("")
        lines.append("**目标市场定位**")
        lines.append("")
        if scenarios:
            lines.append(f"基于现有分析，项目聚焦以下应用场景：【事实】{scenarios}")
        else:
            lines.append("目标市场与应用场景待进一步调研明确。【待验证】")

        lines.append("")
        lines.append("**差异化优势**")
        lines.append("")
        lines.append(
            "本项目的商业定位区别于传统技术路线之处在于："
            "以技术创新为壁垒，以场景深耕为路径，以产业协同为杠杆。"
            "【推断】"
        )

        return "\n".join(lines)

    def _write_bp_ch2_2_4(self, ctx: ChapterWriterContext) -> str:
        """2.4 发展愿景与路线图"""
        heading = self.module_heading(ctx)
        trl_level = self.analysis_field(ctx, "trl_level")

        lines = [heading, ""]

        lines.append("本项目遵循「技术成熟 → 产品落地 → 商业放量」三阶段递进路径。")
        lines.append("")

        lines.append("**第一阶段：技术深耕期**")
        lines.append("")
        if trl_level:
            lines.append(
                f"当前 TRL {trl_level} 为起点，完成核心技术攻关与中试放大验证，"
                f"实现技术参数全面达标。【{'事实' if trl_level else '推断'}】"
            )
        else:
            lines.append(
                "完成核心技术攻关与中试放大验证，实现技术参数全面达标。【待验证】"
            )

        lines.append("")
        lines.append("**第二阶段：产品转化期**")
        lines.append("")
        lines.append(
            "完成产品原型开发与小批量试产，通过试点应用积累运行数据，"
            "建立标准化生产流程与质量体系。【推断】"
        )

        lines.append("")
        lines.append("**第三阶段：商业拓展期**")
        lines.append("")
        lines.append(
            "实现规模化量产，构建覆盖目标市场的渠道网络，"
            "推进产业链上下游协同，达成商业化闭环。【推断】"
        )

        lines.append("")
        lines.append(
            "> 以上各阶段时间节点与里程碑详见配套路线图（甘特图）。"
            "具体时间规划需结合融资节奏与市场反馈动态调整。【待验证】"
        )

        return "\n".join(lines)
