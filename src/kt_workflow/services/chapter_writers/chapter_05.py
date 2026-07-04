"""中游章节 Writer — 第五章 — 商业化落地方案

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_05`，在流水线中的位置：

  … → kt_structure → **kt_chapter_05** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写「怎么卖、怎么赚钱、怎么落地」——商业化方案章，模块最多。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 12 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 4 个），还要返回图表 JSON

你要写的具体内容：12 个小节；其中 5.1.1～5.1.4 四段合计只能 600～800 字，分配字数时注意总预算。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · 5.1 四个子模块别各写很长，否则汇编后超标。
  · 5.2、5.3.1、5.4、5.5.1 都要 chart，优先 mermaid 或 table。
  · 场景、TRL 看 application_scenarios、trl_level。

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
#   - profile.analysis.application_scenarios
#   - profile.analysis.target_market
#   - profile.analysis.commercialization_barriers
#   - profile.analysis.trl_level

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
#   - bp_ch5_5_1_1 | ref=5.1.1 | chart=否 | 5.1 子块
#   - bp_ch5_5_1_2 | ref=5.1.2 | chart=否 | 5.1 子块
#   - bp_ch5_5_1_3 | ref=5.1.3 | chart=否 | 5.1 子块
#   - bp_ch5_5_1_4 | ref=5.1.4 | chart=否 | 5.1 子块
#   - bp_ch5_5_2 | ref=5.2 | chart=是 | 以图为主
#   - bp_ch5_5_3_1 | ref=5.3.1 | chart=是 | 渠道、场景与预期回报
#   - bp_ch5_5_3_2 | ref=5.3.2 | chart=否 | 收费方式
#   - bp_ch5_5_3_3 | ref=5.3.3 | chart=否 | 成本构成
#   - bp_ch5_5_3_4 | ref=5.3.4 | chart=否 | 价值估算依据
#   - bp_ch5_5_3_5 | ref=5.3.5 | chart=否 | 收益与回本测算
#   - bp_ch5_5_4 | ref=5.4 | chart=是 | ≤400
#   - bp_ch5_5_5_1 | ref=5.5.1 | chart=是 | 流程图

字数/篇幅：5.1.1～5.1.4 合计 600～800 字
话术模板：templates.md §五
注册表  ：config/bp_transform_outline_registry.json（chapter=5）
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


class Chapter05Writer(BaseChapterWriter):
    """chapter=5 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 5
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

        if module_id == "bp_ch5_5_1_1":
            return self._write_bp_ch5_5_1_1(ctx)
        if module_id == "bp_ch5_5_1_2":
            return self._write_bp_ch5_5_1_2(ctx)
        if module_id == "bp_ch5_5_1_3":
            return self._write_bp_ch5_5_1_3(ctx)
        if module_id == "bp_ch5_5_1_4":
            return self._write_bp_ch5_5_1_4(ctx)
        if module_id == "bp_ch5_5_2":
            return self._write_bp_ch5_5_2(ctx)
        if module_id == "bp_ch5_5_3_1":
            return self._write_bp_ch5_5_3_1(ctx)
        if module_id == "bp_ch5_5_3_2":
            return self._write_bp_ch5_5_3_2(ctx)
        if module_id == "bp_ch5_5_3_3":
            return self._write_bp_ch5_5_3_3(ctx)
        if module_id == "bp_ch5_5_3_4":
            return self._write_bp_ch5_5_3_4(ctx)
        if module_id == "bp_ch5_5_3_5":
            return self._write_bp_ch5_5_3_5(ctx)
        if module_id == "bp_ch5_5_4":
            return self._write_bp_ch5_5_4(ctx)
        if module_id == "bp_ch5_5_5_1":
            return self._write_bp_ch5_5_5_1(ctx)

        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext) -> ModuleChartSpec:
        """
        【图表入口 — 与 generate_module_text 配对】

        仅当注册表 needs_chart=true 时，chapter_runner 才会调用本函数。
        返回 dict 写入 bp_module_chart，slug 与正文相同（module["id"]）。
        正文写完后，在这里为同一 module_id 返回 table / mermaid / image_ref。
        """
        module_id = ctx["module"].get("id", "")
        if module_id == "bp_ch5_5_2":
            return self._chart_bp_ch5_5_2(ctx)
        if module_id == "bp_ch5_5_3_1":
            return self._chart_bp_ch5_5_3_1(ctx)
        if module_id == "bp_ch5_5_4":
            return self._chart_bp_ch5_5_4(ctx)
        if module_id == "bp_ch5_5_5_1":
            return self._chart_bp_ch5_5_5_1(ctx)
        return self.scaffold_module_chart(ctx)

    def _chart_bp_ch5_5_2(self, ctx: ChapterWriterContext):
        """
        【图表占位】5.2 商业模式
        slug=bp_ch5_5_2（与正文 bp_module_text 相同）
        建议 chart_type: mermaid  writer_hint: 以图为主

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        market = self._label(self._market_phrase(ctx), "目标客户")
        scenario = self._label(self._scenarios_phrase(ctx, 1), "应用场景")
        value = self._label(self._tech_phrase(ctx), "核心价值")
        mermaid = (
            "flowchart LR\n"
            f'    A["目标客户\\n{market}"] --> B["场景切入\\n{scenario}"]\n'
            f'    B --> C["交付内容\\n{value}"]\n'
            '    C --> D["收入来源\\n产品费/服务费/续费"]\n'
            '    D --> E["价值沉淀\\n案例/数据/复购"]'
        )
        return self.mermaid_chart("商业模式闭环图", mermaid)

    def _chart_bp_ch5_5_3_1(self, ctx: ChapterWriterContext):
        """
        【图表占位】5.3.1 渠道、场景与预期回报
        slug=bp_ch5_5_3_1（与正文 bp_module_text 相同）
        建议 chart_type: mermaid  

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        scenarios = self._analysis_points(ctx, "application_scenarios", limit=3)
        rows = []
        channel_defaults = ["行业直销", "生态合作", "示范项目转介绍"]
        return_defaults = [
            "项目成交 + 实施服务",
            "联合方案分成 + 批量复制",
            "案例扩散 + 后续复购",
        ]
        for idx in range(3):
            scenario = scenarios[idx] if idx < len(scenarios) else "【待验证】"
            rows.append(
                [
                    channel_defaults[idx],
                    self._truncate(scenario, 24),
                    return_defaults[idx],
                    "【推断】",
                ]
            )
        return self.table_chart(
            "渠道-场景-回报概览",
            ["渠道", "适配场景", "回报逻辑", "证据状态"],
            rows,
        )

    def _chart_bp_ch5_5_4(self, ctx: ChapterWriterContext):
        """
        【图表占位】5.4 产业布局
        slug=bp_ch5_5_4（与正文 bp_module_text 相同）
        建议 chart_type: mermaid  writer_hint: ≤400

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        market = self._label(self._market_phrase(ctx), "目标行业")
        scenarios = self._label(self._scenarios_phrase(ctx, 2), "重点场景")
        mermaid = (
            "flowchart LR\n"
            '    A["上游资源\\n技术/设备/数据"] --> B["本项目\\n产品化与交付能力"]\n'
            f'    B --> C["主业务\\n{market}"]\n'
            '    B --> D["子业务\\n集成/运维/数据服务"]\n'
            f'    C --> E["示范复制\\n{scenarios}"]\n'
            '    D --> F["生态协同\\n伙伴共建"]'
        )
        return self.mermaid_chart("产业布局协同图", mermaid)

    def _chart_bp_ch5_5_5_1(self, ctx: ChapterWriterContext):
        """
        【图表占位】5.5.1 实施路径
        slug=bp_ch5_5_5_1（与正文 bp_module_text 相同）
        建议 chart_type: mermaid  writer_hint: 流程图

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        trl = self._label(self._trl_phrase(ctx), "成熟度校准")
        mermaid = (
            "flowchart LR\n"
            f'    A["研发定型\\n{trl}"] --> B["试点验证\\n场景适配"]\n'
            '    B --> C["标准化交付\\n方案沉淀"]\n'
            '    C --> D["渠道推广\\n合作复制"]\n'
            '    D --> E["规模运营\\n复购扩张"]'
        )
        return self.mermaid_chart("商业化实施路径图", mermaid)

    # ------------------------------------------------------------------
    # 正文私有方法（每个模块一个）与通用辅助函数
    # ------------------------------------------------------------------
    def _write_bp_ch5_5_1_1(self, ctx: ChapterWriterContext) -> str:
        tech = self._tech_phrase(ctx)
        market = self._market_phrase(ctx)
        summary = self._analysis_sentence(ctx, "summary", 70)
        return self._compose_module(
            ctx,
            (
                f"【事实】{tech}围绕{market}形成可交付的产品化载体，"
                "建议以“标准能力模块 + 场景方案 + 实施服务”的组合方式进入市场。"
            ),
            (
                f"【事实】{summary}"
                if summary != "【待验证】"
                else "【待验证】材料尚未充分披露标准产品形态、交付边界与客户验收口径。"
            ),
        )

    def _write_bp_ch5_5_1_2(self, ctx: ChapterWriterContext) -> str:
        scenarios = self._scenarios_phrase(ctx, 3)
        return self._compose_module(
            ctx,
            f"【事实】优先落地场景可聚焦于{scenarios}，优先选择需求明确、效果可量化、便于形成示范案例的应用环节。",
            "【推断】建议先从 2～3 个高频场景切入，完成首批样板后再向相邻行业或更复杂场景横向复制。",
        )

    def _write_bp_ch5_5_1_3(self, ctx: ChapterWriterContext) -> str:
        trl = self._trl_phrase(ctx)
        rationale = self._analysis_sentence(ctx, "trl_rationale", 72)
        return self._compose_module(
            ctx,
            f"【事实】当前技术成熟度可参考{trl}，说明项目已具备一定的产品化或试点验证基础，但仍需结合客户现场条件完成交付校准。",
            (
                f"【事实】{rationale}"
                if rationale != "【待验证】"
                else "【待验证】缺少成熟度判定依据、测试样本与稳定性验证结果，暂不宜直接承诺全面规模化落地。"
            ),
        )

    def _write_bp_ch5_5_1_4(self, ctx: ChapterWriterContext) -> str:
        barriers = self._barrier_phrase(ctx, 3)
        return self._compose_module(
            ctx,
            f"【事实】商业化边界主要受{barriers}等因素影响，落地前需同步确认客户侧数据、设备、流程和合规条件是否满足实施要求。",
            "【推断】应将超出现阶段能力的个性化需求、跨系统改造和长周期验证任务单独列项，避免在售前阶段过度承诺。",
        )

    def _write_bp_ch5_5_2(self, ctx: ChapterWriterContext) -> str:
        scenarios = self._scenarios_phrase(ctx, 2)
        market = self._market_phrase(ctx)
        return self._compose_module(
            ctx,
            f"【事实】商业模式建议围绕{scenarios}切入{market}，以前端场景方案获客、中端产品化能力交付、后端实施与持续服务变现形成闭环。",
            "【推断】当示范案例形成后，可进一步叠加升级服务、数据服务或联合解决方案分成，放大单客户生命周期价值。",
        )

    def _write_bp_ch5_5_3_1(self, ctx: ChapterWriterContext) -> str:
        market = self._market_phrase(ctx)
        scenarios = self._scenarios_phrase(ctx, 3)
        return self._compose_module(
            ctx,
            f"【事实】渠道优先顺序建议为行业直销、生态合作伙伴和示范项目转介绍，重点服务{market}中的{scenarios}等典型场景。",
            "【推断】预期回报不仅来自首次成交，也来自实施服务、运维续费和跨场景复制；具体转化效率仍需试点订单验证。",
        )

    def _write_bp_ch5_5_3_2(self, ctx: ChapterWriterContext) -> str:
        return self._compose_module(
            ctx,
            "【事实】收费方式宜采用“基础交付费 + 实施服务费 + 持续运维/升级费”的组合结构，以覆盖前期部署、后期服务和功能迭代成本。",
            "【推断】若客户更偏结果导向，可补充按使用量、按里程碑或按绩效结算的弹性条款，以提升签约适配性。",
        )

    def _write_bp_ch5_5_3_3(self, ctx: ChapterWriterContext) -> str:
        barriers = self._barrier_phrase(ctx, 2)
        return self._compose_module(
            ctx,
            "【事实】成本构成主要包括研发迭代、软硬件或设备投入、项目实施交付、渠道拓展以及售后服务保障等部分。",
            f"【推断】前期受{barriers}等因素影响，单项目人力和验证投入会相对较高；随着模板化程度提升，边际交付成本有望下降。",
        )

    def _write_bp_ch5_5_3_4(self, ctx: ChapterWriterContext) -> str:
        scenarios = self._scenarios_phrase(ctx, 2)
        return self._compose_module(
            ctx,
            f"【事实】价值估算应围绕{scenarios}中的客户痛点展开，从降本、提效、合规、质量稳定性或新增收入等维度建立量化口径。",
            "【推断】建议将现有人工流程、替代方案或行业平均水平设为对照组，形成可复核的 ROI 与投资决策依据。",
        )

    def _write_bp_ch5_5_3_5(self, ctx: ChapterWriterContext) -> str:
        gap_note = self._data_gap_sentence(ctx)
        return self._compose_module(
            ctx,
            "【推断】收益测算可按“试点项目收入 + 标准化复制收入 + 服务续费收入”三层展开，回本周期主要取决于首单获取成本、交付复杂度和复购速度。",
            f"【待验证】{gap_note}",
        )

    def _write_bp_ch5_5_4(self, ctx: ChapterWriterContext) -> str:
        market = self._market_phrase(ctx)
        scenarios = self._scenarios_phrase(ctx, 2)
        return self._compose_module(
            ctx,
            f"【事实】产业布局应围绕“核心能力自持、关键资源协同、重点场景突破”展开，上游对接技术与资源，中游沉淀产品化与交付能力，下游锁定{market}中的{scenarios}等示范客户。",
            "【推断】短期宜聚焦主业务闭环，子业务可延伸至集成服务、运维服务或数据增值服务，以增强产业链协同深度。",
        )

    def _write_bp_ch5_5_5_1(self, ctx: ChapterWriterContext) -> str:
        trl = self._trl_phrase(ctx)
        barriers = self._barrier_phrase(ctx, 2)
        return self._compose_module(
            ctx,
            f"【事实】实施路径建议按“研发定型 → 试点验证 → 标准化交付 → 渠道推广 → 规模复制”推进，并以{trl}作为节点评估的成熟度参照。",
            f"【推断】每一阶段都应同步校准{barriers}等关键约束，把验证结果沉淀为标准方案、交付模板和复用案例。",
        )

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
        if summary != "【待验证】":
            return summary
        return "该成果"

    def _market_phrase(self, ctx: ChapterWriterContext) -> str:
        market_points = self._analysis_points(ctx, "target_market", limit=2)
        if market_points == ["【待验证】"]:
            return "目标市场"
        return "、".join(self._truncate(item, 24) for item in market_points)

    def _scenarios_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        scenario_points = self._analysis_points(ctx, "application_scenarios", limit=limit)
        if scenario_points == ["【待验证】"]:
            return "【待验证】场景"
        return "、".join(self._truncate(item, 22) for item in scenario_points)

    def _trl_phrase(self, ctx: ChapterWriterContext) -> str:
        trl = self._analysis_sentence(ctx, "trl_level", 24)
        return trl if trl != "【待验证】" else "【待验证】成熟度"

    def _barrier_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        barrier_points = self._analysis_points(ctx, "commercialization_barriers", limit=limit)
        if barrier_points == ["【待验证】"]:
            return "市场验证、交付条件与合规要求"
        return "、".join(self._truncate(item, 22) for item in barrier_points)

    def _data_gap_sentence(self, ctx: ChapterWriterContext) -> str:
        gaps = self._flatten_points(self._analysis_value(ctx, "data_gaps"))
        if gaps:
            return "当前仍缺少" + "、".join(self._truncate(item, 20) for item in gaps[:3]) + "等关键输入。"
        return "当前仍缺少客单价、毛利率、签约节奏和复购率等关键输入。"

    def _flatten_points(self, value: Any) -> list[str]:
        points: list[str] = []
        self._collect_points(value, points)
        unique_points: list[str] = []
        seen: set[str] = set()
        for point in points:
            cleaned = self._clean(point)
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                unique_points.append(cleaned)
        return unique_points

    def _collect_points(self, value: Any, points: list[str]) -> None:
        if value is None:
            return
        if isinstance(value, (str, int, float, bool)):
            for part in re.split(r"[\n；;]+", str(value)):
                cleaned = self._clean(part)
                if cleaned:
                    points.append(cleaned)
            return
        if isinstance(value, dict):
            preferred_scalar_keys = (
                "summary",
                "description",
                "desc",
                "overview",
                "value",
                "content",
                "text",
                "name",
                "title",
                "scenario",
                "market",
                "channel",
                "rationale",
                "level",
            )
            preferred_nested_keys = (
                "items",
                "list",
                "points",
                "scenarios",
                "applications",
                "channels",
                "advantages",
                "barriers",
                "steps",
                "stages",
                "phases",
                "details",
            )
            for key in preferred_scalar_keys:
                if key in value:
                    self._collect_points(value.get(key), points)
            for key in preferred_nested_keys:
                if key in value:
                    self._collect_points(value.get(key), points)
            if not points:
                for key, nested_value in list(value.items())[:4]:
                    summary = self._first_point(nested_value)
                    if summary:
                        points.append(f"{key}：{self._truncate(summary, 24)}")
            return
        if isinstance(value, (list, tuple, set)):
            for item in value:
                self._collect_points(item, points)

    def _first_point(self, value: Any) -> str:
        points = self._flatten_points(value)
        return points[0] if points else ""

    def _label(self, text: str, fallback: str) -> str:
        cleaned = self._clean(text)
        if not cleaned or cleaned.startswith("【待验证】"):
            return fallback
        return re.sub(r'["\[\]\{\}`]', "", self._truncate(cleaned, 18))

    def _truncate(self, text: str, max_chars: int) -> str:
        cleaned = self._clean(text)
        if not cleaned:
            return ""
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[: max_chars - 1].rstrip("，,；;。 ") + "…"

    def _clean(self, text: Any) -> str:
        return re.sub(r"\s+", " ", str(text)).strip()
