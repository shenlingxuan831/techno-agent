"""中游章节 Writer — 第九章 — 结论与展望

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_09`，在流水线中的位置：

  … → kt_structure → **kt_chapter_09** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写「收尾三段」：能不能做、价值是什么、以后怎样。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 3 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 0 个），还要返回图表 JSON

你要写的具体内容：3 个小节，字数紧（9.1≤300，9.2/9.3≤200）。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · 9.1 可行性结论要和前面风险、TRL 一致，不要自相矛盾。
  · 可大量复用 analysis.summary 和 advantages，但要压缩字数。

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
#   - profile.analysis.advantages
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
#   - bp_ch9_9_1 | ref=9.1 | chart=否 | 项目可行性结论
#   - bp_ch9_9_2 | ref=9.2 | chart=否 | 核心价值总结
#   - bp_ch9_9_3 | ref=9.3 | chart=否 | 未来展望

字数/篇幅：9.1 ≤300；9.2/9.3 ≤200
话术模板：templates.md §九
注册表  ：config/bp_transform_outline_registry.json（chapter=9）
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

from typing import Any

from kt_workflow.services.chapter_writer_contract import ChapterWriterContext, ModuleChartSpec
from kt_workflow.services.chapter_writers._base import BaseChapterWriter


class Chapter09Writer(BaseChapterWriter):
    """chapter=9 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 9
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
        mod = ctx["module"]
        module_id = mod.get("id", "")

        if module_id == "bp_ch9_9_1":
            return self._write_bp_ch9_9_1(ctx)
        if module_id == "bp_ch9_9_2":
            return self._write_bp_ch9_9_2(ctx)
        if module_id == "bp_ch9_9_3":
            return self._write_bp_ch9_9_3(ctx)

        # 未实现的模块仍返回占位（方便联调；全部实现后可删）
        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext):
        """本章无 needs_chart 模块。"""
        return None

    # ------------------------------------------------------------------
    # 正文私有方法示例（每个模块一个）：
    #
    # def _write_bp_ch9_9_1(self, ctx: ChapterWriterContext) -> str:
    #     """写 项目可行性结论 小节。"""
    #     heading = self.module_heading(ctx)
    #     summary = self.analysis_field(ctx, "summary")
    #     return f"{heading}\n\n{summary}\n"
    #
    # 图表私有方法见上方 _chart_* （与 needs_chart 模块一一对应）
    # ------------------------------------------------------------------

    def _write_bp_ch9_9_1(self, ctx: ChapterWriterContext) -> str:
        """写 9.1 项目可行性结论。"""
        heading = self.module_heading(ctx)
        tech_name = self._tech_name(ctx)
        summary = self._field(ctx, "summary", "材料尚未形成完整成果概述，需结合原始技术文档进一步补充。")
        trl = self._trl(ctx)
        advantages = self._items(ctx, "advantages")[:2]
        barriers = self._items(ctx, "commercialization_barriers")[:2]
        gaps = self._items(ctx, "data_gaps")[:3]

        adv_text = "；".join(advantages) if advantages else "已有材料显示具备一定技术积累和场景适配基础"
        barrier_text = "；".join(barriers) if barriers else "产业化验证、客户试点和成本收益数据仍需补充"
        gap_text = self._gap_sentence(gaps)

        return (
            f"{heading}\n\n"
            f"【事实】{tech_name}的现有材料显示：{summary}\n\n"
            f"【推断】结合当前成熟度（{trl}）和已呈现优势（{adv_text}），项目具备进入科研成果转化论证与小规模应用验证的阶段性可行性。"
            f"但其商业化结论应保持审慎，重点约束在{barrier_text}。建议将本项目定位为“可推进、需验证”的成果转化项目，优先完成中试/试点、知识产权权属、客户需求和成本模型的闭环验证。\n\n"
            f"> 【待验证】{gap_text}\n"
        )

    def _write_bp_ch9_9_2(self, ctx: ChapterWriterContext) -> str:
        """写 9.2 核心价值总结。"""
        heading = self.module_heading(ctx)
        tech_name = self._tech_name(ctx)
        advantages = self._items(ctx, "advantages")[:3]
        scenarios = self._items(ctx, "application_scenarios")[:2]
        market = self._field(ctx, "target_market", "目标市场边界尚待进一步明确")

        value_points = advantages or ["提升相关场景的技术效率或性能表现", "为后续产业化合作提供可验证的技术基础"]
        scenario_text = "；".join(scenarios) if scenarios else "具体落地场景仍需结合客户需求筛选"
        value_lines = "\n".join(f"- 【事实/推断】{point}" for point in value_points)

        return (
            f"{heading}\n\n"
            f"{tech_name}的核心价值不在于把科研成果直接包装成成熟产品，而在于把已有技术能力转化为可被评审、合作方和投资方理解的落地假设。\n\n"
            f"{value_lines}\n\n"
            f"【推断】面向{market}，项目后续价值释放应围绕“{scenario_text}”展开，通过验证数据、试点案例和成本收益测算逐步证明其商业可行性。\n"
        )

    def _write_bp_ch9_9_3(self, ctx: ChapterWriterContext) -> str:
        """写 9.3 未来展望。"""
        heading = self.module_heading(ctx)
        tech_name = self._tech_name(ctx)
        gaps = self._items(ctx, "data_gaps")[:4]
        policy = self._field(ctx, "policy_fit_hint", "政策与资质匹配方向仍需补充")
        gap_text = "；".join(gaps) if gaps else "验证数据、客户试点、财务假设和合作资源"

        return (
            f"{heading}\n\n"
            f"下一阶段，{tech_name}应以“补证据、做试点、定边界”为主线推进。短期重点是补齐{gap_text}等材料，形成可复核的实验和应用证明；中期应选择1-2个高匹配场景开展联合验证，沉淀交付流程、成本结构和知识产权使用规则；长期则结合{policy}，逐步扩展产业合作、政策申报和资本对接。\n\n"
            f"> 【待验证】未来规划中的时间表、预算、客户名单和收入目标，应在取得真实试点或合作材料后再写入正式 BP。\n"
        )

    def _tech_name(self, ctx: ChapterWriterContext) -> str:
        return self._field(
            ctx,
            "tech_name",
            self.submission_field(ctx, "project_name", "本项目"),
        )

    def _trl(self, ctx: ChapterWriterContext) -> str:
        profile = ctx.get("profile") or {}
        content = profile.get("content") or {}
        return self._field(ctx, "trl_level", str(content.get("trl_hint") or "待验证"))

    def _field(self, ctx: ChapterWriterContext, key: str, default: str = "") -> str:
        value = self.analysis_field(ctx, key, default)
        return self._clean(value) or default

    def _items(self, ctx: ChapterWriterContext, key: str) -> list[str]:
        analysis = (ctx.get("profile") or {}).get("analysis") or {}
        raw = analysis.get(key)
        if isinstance(raw, list):
            return [self._clean(item) for item in raw if self._clean(item)]
        text = self._clean(raw)
        if not text:
            return []
        chunks = [p.strip(" ;；,，、") for p in text.replace("\n", "；").split("；")]
        return [p for p in chunks if p]

    @staticmethod
    def _clean(value: Any) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        return " ".join(text.split())

    @staticmethod
    def _gap_sentence(gaps: list[str]) -> str:
        if not gaps:
            return "尚需补充关键验证材料；未取得依据前，不应写入确定性的融资额、收入目标、客户案例或政策名称。"
        return "；".join(gaps) + "；未取得依据前，不应写入确定性的融资额、收入目标、客户案例或政策名称。"
