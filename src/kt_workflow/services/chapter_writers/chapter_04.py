"""中游章节 Writer — 第四章 — 市场分析

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_04`，在流水线中的位置：

  … → kt_structure → **kt_chapter_04** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写「市场大环境、规模、客户、竞品」——回答「有没有市场」。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 6 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 4 个），还要返回图表 JSON

你要写的具体内容：6 个小节；整章 ≤2000 字；多个小节要带 chart（TAM 表、画像表、竞品表等）。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · target_market、competitive_landscape 是主素材；数字无来源必须【待验证】。
  · 4.2 TAM/SAM/SOM 用 table_chart 生成表格 spec 最省事。

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
#   - profile.analysis.target_market
#   - profile.analysis.competitive_landscape
#   - profile.analysis.application_scenarios
#   - profile.analysis.policy_fit_hint

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
  · 本章需实现图表的模块数：4  → 见下方 _chart_* 方法
  · JSON 规范：config/kt_chapter_chart_spec_schema.json

================================================================================
【本章模块清单（slug = id，勿改）】
================================================================================
#   - bp_ch4_4_1 | ref=4.1 | chart=是 | ≤400
#   - bp_ch4_4_2 | ref=4.2 | chart=是 | ≤300
#   - bp_ch4_4_3 | ref=4.3 | chart=是 | 画像表
#   - bp_ch4_4_4 | ref=4.4 | chart=否 | ≤300
#   - bp_ch4_4_5 | ref=4.5 | chart=是 | ≤500
#   - bp_ch4_4_6 | ref=4.6 | chart=否 | ≤300

字数/篇幅：整章 ≤2000 字
话术模板：templates.md §四
注册表  ：config/bp_transform_outline_registry.json（chapter=4）
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

import re
from typing import Any

from kt_workflow.services.chapter_writer_contract import ChapterWriterContext, ModuleChartSpec
from kt_workflow.services.chapter_writers._base import BaseChapterWriter


class Chapter04Writer(BaseChapterWriter):
    """chapter=4 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 4
    IMPLEMENTER_MODULE = __name__

    def generate_module_text(self, ctx: ChapterWriterContext) -> str:
        mod = ctx["module"]
        module_id = mod.get("id", "")

        writers = {
            "bp_ch4_4_1": self._write_bp_ch4_4_1,
            "bp_ch4_4_2": self._write_bp_ch4_4_2,
            "bp_ch4_4_3": self._write_bp_ch4_4_3,
            "bp_ch4_4_4": self._write_bp_ch4_4_4,
            "bp_ch4_4_5": self._write_bp_ch4_4_5,
            "bp_ch4_4_6": self._write_bp_ch4_4_6,
        }
        if module_id in writers:
            return writers[module_id](ctx)
        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext):
        """
        【图表入口 — 与 generate_module_text 配对】

        仅当注册表 needs_chart=true 时，chapter_runner 才会调用本函数。
        返回 dict 写入 bp_module_chart，slug 与正文相同（module["id"]）。
        正文写完后，在这里为同一 module_id 返回 table / mermaid / image_ref。
        """
        module_id = ctx["module"].get("id", "")
        if module_id == "bp_ch4_4_1":
            return self._chart_bp_ch4_4_1(ctx)
        if module_id == "bp_ch4_4_2":
            return self._chart_bp_ch4_4_2(ctx)
        if module_id == "bp_ch4_4_3":
            return self._chart_bp_ch4_4_3(ctx)
        if module_id == "bp_ch4_4_5":
            return self._chart_bp_ch4_4_5(ctx)
        return self.scaffold_module_chart(ctx)

    def _chart_bp_ch4_4_1(self, ctx: ChapterWriterContext):
        market = self._safe_label(self._market_phrase(ctx), "目标行业")
        mermaid_src = (
            "flowchart LR\n"
            "    subgraph PEST[\"宏观环境 PEST\"]\n"
            "        P[政策/监管]\n"
            "        E[经济/资本]\n"
            "        S[社会/需求]\n"
            "        T[技术/创新]\n"
            "    end\n"
            "    subgraph CHAIN[\"产业链\"]\n"
            "        U[上游\\n数据/算力/设备] --> M[中游\\n算法/平台/集成]\n"
            f"        M --> D[下游\\n{market}]\n"
            "    end\n"
            "    P --> CHAIN\n"
            "    E --> CHAIN\n"
            "    S --> CHAIN\n"
            "    T --> CHAIN"
        )
        return self.mermaid_chart("行业 PEST 与产业链结构", mermaid_src)

    def _chart_bp_ch4_4_2(self, ctx: ChapterWriterContext):
        market = self._market_phrase(ctx)
        rows = [
            ["TAM（总体市场）", "【待验证】", "【待验证】", f"覆盖{market}相关整体需求空间"],
            ["SAM（可服务市场）", "【待验证】", "【待验证】", "与项目能力边界匹配的可触达细分"],
            ["SOM（可获得市场）", "【待验证】", "【待验证】", "3～5 年内可合理获取的份额"],
        ]
        return self.table_chart(
            "市场规模测算（TAM / SAM / SOM）",
            ["层级", "规模估算", "增速/口径", "说明"],
            rows,
        )

    def _chart_bp_ch4_4_3(self, ctx: ChapterWriterContext):
        user_type = self.submission_field(ctx, "user_type", "目标客户")
        scenarios = self._scenarios_phrase(ctx, 2)
        rows = [
            ["核心客户类型", user_type if user_type != "【待验证】" else "【待验证】", "决策链与采购模式待补充"],
            ["典型应用场景", scenarios, "优先选择可量化 ROI 的场景切入"],
            ["关键痛点", self._pain_phrase(ctx, 2), "来自材料归纳或访谈验证"],
            ["预算/支付意愿", "【待验证】", "需结合试点报价与客户反馈"],
            ["触达渠道", "行业直销、生态合作、示范项目", "【推断】"],
        ]
        return self.table_chart("目标客户画像", ["维度", "描述", "备注"], rows)

    def _chart_bp_ch4_4_5(self, ctx: ChapterWriterContext):
        competitors = self._competitor_rows(ctx)
        porter_rows = [
            ["现有竞争者", self._landscape_phrase(ctx, 1), "【待验证】"],
            ["潜在进入者", "通用 AI 平台、垂直 SaaS 厂商", "【推断】"],
            ["替代品威胁", self._scenarios_phrase(ctx, 1), "【推断】"],
            ["买方议价能力", "【待验证】", "取决于客户集中度与标准化程度"],
            ["供方议价能力", "算力、数据、核心人才", "【推断】"],
        ]
        rows = porter_rows + [["—", "—", "—"]] + competitors
        return self.table_chart(
            "竞争格局（波特五力 + 竞品对比）",
            ["维度/竞品", "现状判断", "证据状态"],
            rows,
        )

    # ------------------------------------------------------------------
    # 正文私有方法
    # ------------------------------------------------------------------

    def _write_bp_ch4_4_1(self, ctx: ChapterWriterContext) -> str:
        market = self._market_phrase(ctx)
        policy = self._analysis_sentence(ctx, "policy_fit_hint", 80)
        summary = self._analysis_sentence(ctx, "summary", 90)
        return self._compose_module(
            ctx,
            f"【推断】{market}所在赛道受政策引导、技术迭代与下游数字化需求共同驱动，"
            "宏观环境整体有利于具备可验证技术方案的成果转化。",
            (
                f"【事实】{policy}"
                if policy not in ("【待验证】", "待验证", "")
                else "【待验证】尚未取得权威政策文件或行业统计的直接引用，PEST 判断需后续补证。"
            ),
            (
                f"【事实】材料显示：{summary}"
                if summary != "【待验证】"
                else "【推断】产业链上中游以算法能力、平台集成与场景交付为主，下游以行业客户价值兑现为关键。"
            ),
        )

    def _write_bp_ch4_4_2(self, ctx: ChapterWriterContext) -> str:
        market = self._market_phrase(ctx)
        return self._compose_module(
            ctx,
            f"【推断】{market}具备持续扩容潜力，但具体 TAM/SAM/SOM 需以第三方行业报告或客户样本订单交叉验证。",
            "【待验证】当前材料未提供可溯源的市场规模数字与增速口径，表中数值暂以【待验证】标注。",
            "【推断】建议以 2～3 个标杆场景的单客户价值 × 可触达客户数做自下而上测算，并与自上而下行业数据对账。",
        )

    def _write_bp_ch4_4_3(self, ctx: ChapterWriterContext) -> str:
        user_type = self.submission_field(ctx, "user_type", "")
        scenarios = self._scenarios_phrase(ctx, 3)
        customer = user_type or "行业机构客户"
        return self._compose_module(
            ctx,
            f"【事实】优先服务对象为{customer}，重点场景包括{scenarios}。",
            "【推断】客户采购通常关注效果可量化、部署边界清晰、合规与数据安全可控，"
            "决策链涉及业务负责人、技术负责人与采购/法务多方协同。",
            "【待验证】客单价区间、采购周期与复购率需通过试点项目进一步校准。",
        )

    def _write_bp_ch4_4_4(self, ctx: ChapterWriterContext) -> str:
        barriers = self._barrier_phrase(ctx, 3)
        disadvantages = self._analysis_points(ctx, "disadvantages", limit=2)
        pain_items = disadvantages if disadvantages != ["【待验证】"] else [barriers]
        pain_text = "；".join(self._truncate(p, 36) for p in pain_items)
        return self._compose_module(
            ctx,
            f"【推断】目标客户在{self._market_phrase(ctx)}中普遍面临{pain_text}等痛点，"
            "现有方案往往在效果稳定性、可解释性或落地成本上存在缺口。",
            "【事实】上述痛点与材料中披露的技术短板、验证不足或商业化障碍相呼应。",
            "【推断】本项目若能在关键场景形成可复核的效能提升，将显著缩短客户决策与采购周期。",
        )

    def _write_bp_ch4_4_5(self, ctx: ChapterWriterContext) -> str:
        tech = self._tech_phrase(ctx)
        landscape = self._landscape_phrase(ctx, 2)
        advantages = self._analysis_points(ctx, "advantages", limit=2)
        adv_text = "、".join(self._truncate(a, 28) for a in advantages) if advantages != ["【待验证】"] else "差异化技术能力"
        return self._compose_module(
            ctx,
            f"【推断】{landscape}构成主要竞争参照，市场呈现「通用平台 + 垂直场景方案」并存的格局。",
            f"【事实】{tech}在{adv_text}等方面具备差异化基础，但仍需通过标杆案例证明相对优势。",
            "【待验证】竞品价格、交付周期与市场份额缺少公开可核对数据，对比结论需后续尽调补充。",
        )

    def _write_bp_ch4_4_6(self, ctx: ChapterWriterContext) -> str:
        market = self._market_phrase(ctx)
        trl = self._analysis_sentence(ctx, "trl_level", 16)
        policy = self._analysis_sentence(ctx, "policy_fit_hint", 60)
        trl_note = f"TRL {trl}" if trl != "【待验证】" else "当前成熟度"
        return self._compose_module(
            ctx,
            f"【推断】从钻石模型看，{market}在需求条件与相关产业支撑方面具备转化土壤，"
            f"项目需同步强化企业战略、要素禀赋与{trl_note}对应的交付能力。",
            (
                f"【事实】{policy}"
                if policy not in ("【待验证】", "待验证", "")
                else "【待验证】政策适配方向需结合属地申报指南与资质要求进一步确认。"
            ),
            "【推断】落地条件包括：明确试点场景、可量化验收指标、合规的数据与算力保障，以及可持续的商业化团队配置。",
        )

    # ------------------------------------------------------------------
    # 通用辅助
    # ------------------------------------------------------------------

    def _compose_module(self, ctx: ChapterWriterContext, *paragraphs: str) -> str:
        heading = self.module_heading(ctx)
        body = [heading]
        for paragraph in paragraphs:
            cleaned = self._clean(paragraph)
            if cleaned:
                body.append(cleaned)
        return "\n\n".join(body) + "\n"

    def _analysis_data(self, ctx: ChapterWriterContext) -> dict[str, Any]:
        profile = ctx.get("profile") or {}
        if not isinstance(profile, dict):
            return {}
        analysis = profile.get("analysis") or {}
        return analysis if isinstance(analysis, dict) else {}

    def _analysis_value(self, ctx: ChapterWriterContext, field: str) -> Any:
        return self._analysis_data(ctx).get(field)

    def _analysis_points(self, ctx: ChapterWriterContext, field: str, limit: int = 3) -> list[str]:
        points = self._flatten_points(self._analysis_value(ctx, field))
        if not points:
            return ["【待验证】"]
        return points[:limit]

    def _analysis_sentence(self, ctx: ChapterWriterContext, field: str, max_chars: int = 72) -> str:
        value = self._analysis_value(ctx, field)
        point = self._first_point(value)
        return self._truncate(point, max_chars) if point else "【待验证】"

    def _tech_phrase(self, ctx: ChapterWriterContext) -> str:
        tech_name = self._analysis_sentence(ctx, "tech_name", 28)
        if tech_name != "【待验证】":
            return tech_name
        summary = self._analysis_sentence(ctx, "summary", 28)
        return summary if summary != "【待验证】" else "本项目成果"

    def _market_phrase(self, ctx: ChapterWriterContext) -> str:
        market_points = self._analysis_points(ctx, "target_market", limit=2)
        if market_points == ["【待验证】"]:
            return "目标细分市场"
        return "、".join(self._truncate(item, 24) for item in market_points)

    def _scenarios_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        scenario_points = self._analysis_points(ctx, "application_scenarios", limit=limit)
        if scenario_points == ["【待验证】"]:
            return "【待验证】典型场景"
        return "、".join(self._truncate(item, 22) for item in scenario_points)

    def _landscape_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        points = self._analysis_points(ctx, "competitive_landscape", limit=limit)
        if points == ["【待验证】"]:
            return "同类技术方案与替代产品"
        return "、".join(self._truncate(item, 26) for item in points)

    def _barrier_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        points = self._analysis_points(ctx, "commercialization_barriers", limit=limit)
        if points == ["【待验证】"]:
            return "验证数据不足、交付复杂度高、客户教育成本"
        return "、".join(self._truncate(item, 22) for item in points)

    def _pain_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        points = self._analysis_points(ctx, "disadvantages", limit=limit)
        if points == ["【待验证】"]:
            return self._barrier_phrase(ctx, limit)
        return "、".join(self._truncate(item, 22) for item in points)

    def _competitor_rows(self, ctx: ChapterWriterContext) -> list[list[str]]:
        points = self._flatten_points(self._analysis_value(ctx, "competitive_landscape"))
        if not points:
            return [
                ["竞品 A（代表方案）", "【待验证】", "【待验证】"],
                ["竞品 B（替代路径）", "【待验证】", "【待验证】"],
                ["本项目", self._tech_phrase(ctx), "【事实/推断】"],
            ]
        rows: list[list[str]] = []
        for idx, name in enumerate(points[:4], start=1):
            rows.append([f"竞品/方案 {idx}：{self._truncate(name, 30)}", "【待验证】", "【待验证】"])
        rows.append(["本项目", self._tech_phrase(ctx), "【事实/推断】"])
        return rows

    def _flatten_points(self, value: Any) -> list[str]:
        points: list[str] = []
        self._collect_points(value, points)
        unique: list[str] = []
        seen: set[str] = set()
        for point in points:
            cleaned = self._clean(point)
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                unique.append(cleaned)
        return unique

    def _collect_points(self, value: Any, points: list[str]) -> None:
        if value is None:
            return
        if isinstance(value, str):
            for part in re.split(r"[；;\n]+", value):
                cleaned = self._clean(part)
                if cleaned:
                    points.append(cleaned)
            return
        if isinstance(value, dict):
            for key in ("name", "title", "label", "description", "summary"):
                if key in value and value[key]:
                    points.append(str(value[key]))
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                self._collect_points(item, points)

    def _first_point(self, value: Any) -> str:
        points = self._flatten_points(value)
        return points[0] if points else ""

    def _safe_label(self, text: str, fallback: str) -> str:
        cleaned = re.sub(r'["\[\]\{\}`]', "", self._truncate(text, 16))
        return cleaned or fallback

    def _truncate(self, text: str, max_chars: int) -> str:
        cleaned = self._clean(text)
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[: max_chars - 1].rstrip("，,；;。 ") + "…"

    def _clean(self, text: Any) -> str:
        return re.sub(r"\s+", " ", str(text)).strip()
