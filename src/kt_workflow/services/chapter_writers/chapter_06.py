"""中游章节 Writer — 第六章 — 运营团队与组织规划

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_06`，在流水线中的位置：

  … → kt_structure → **kt_chapter_06** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写「谁来做、有什么资源、专利和竞品优势」。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 5 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 3 个），还要返回图表 JSON

你要写的具体内容：5 个小节；整章 ≤800 字；6.1/6.3/6.5 需要 chart。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · team_and_resources、ip_status 是主素材；人名职称材料没有就别编。
  · 6.4 侧重组织与专利布局，与 3.6 技术壁垒区分开。

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
#   - profile.analysis.team_and_resources
#   - profile.analysis.ip_status
#   - profile.analysis.advantages
#   - profile.analysis.competitive_landscape

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
  · 本章需实现图表的模块数：3  → 见下方 _chart_* 方法
  · JSON 规范：config/kt_chapter_chart_spec_schema.json

================================================================================
【本章模块清单（slug = id，勿改）】
================================================================================
#   - bp_ch6_6_1 | ref=6.1 | chart=是 | 履历表
#   - bp_ch6_6_2 | ref=6.2 | chart=否 | 顾问团队
#   - bp_ch6_6_3 | ref=6.3 | chart=是 | ≤400
#   - bp_ch6_6_4 | ref=6.4 | chart=否 | 组织侧 IP；非 3.6 重复
#   - bp_ch6_6_5 | ref=6.5 | chart=是 | 双视角竞品

字数/篇幅：整章 ≤800 字；6.3 ≤400；6.4 ≤300
话术模板：templates.md §六
注册表  ：config/bp_transform_outline_registry.json（chapter=6）
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


class Chapter06Writer(BaseChapterWriter):
    """chapter=6 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 6
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

        if module_id == "bp_ch6_6_1":
            return self._write_bp_ch6_6_1(ctx)
        if module_id == "bp_ch6_6_2":
            return self._write_bp_ch6_6_2(ctx)
        if module_id == "bp_ch6_6_3":
            return self._write_bp_ch6_6_3(ctx)
        if module_id == "bp_ch6_6_4":
            return self._write_bp_ch6_6_4(ctx)
        if module_id == "bp_ch6_6_5":
            return self._write_bp_ch6_6_5(ctx)

        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext) -> ModuleChartSpec:
        """
        【图表入口 — 与 generate_module_text 配对】

        仅当注册表 needs_chart=true 时，chapter_runner 才会调用本函数。
        返回 dict 写入 bp_module_chart，slug 与正文相同（module["id"]）。
        正文写完后，在这里为同一 module_id 返回 table / mermaid / image_ref。
        """
        module_id = ctx["module"].get("id", "")
        if module_id == "bp_ch6_6_1":
            return self._chart_bp_ch6_6_1(ctx)
        if module_id == "bp_ch6_6_3":
            return self._chart_bp_ch6_6_3(ctx)
        if module_id == "bp_ch6_6_5":
            return self._chart_bp_ch6_6_5(ctx)
        return self.scaffold_module_chart(ctx)

    def _chart_bp_ch6_6_1(self, ctx: ChapterWriterContext):
        """
        【图表占位】6.1 核心团队
        slug=bp_ch6_6_1（与正文 bp_module_text 相同）
        建议 chart_type: table  writer_hint: 履历表

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        rows = []
        team_points = self._team_points(ctx, limit=3)
        for idx in range(3):
            member = team_points[idx] if idx < len(team_points) else "【待验证】"
            rows.append(
                [
                    f"核心成员{idx + 1}",
                    self._truncate(member, 24),
                    "研发/产业化/市场推进",
                    "【待验证】",
                ]
            )
        return self.table_chart("核心团队履历表", ["成员", "履历或优势", "当前职责", "证据状态"], rows)

    def _chart_bp_ch6_6_3(self, ctx: ChapterWriterContext):
        """
        【图表占位】6.3 资源优势
        slug=bp_ch6_6_3（与正文 bp_module_text 相同）
        建议 chart_type: image_ref  writer_hint: ≤400

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        advantage = self._label(self._advantages_phrase(ctx, 1), "资源能力")
        ip = self._label(self._ip_phrase(ctx, 1), "知识产权")
        mermaid = (
            "flowchart LR\n"
            f'    A["团队基础\\n{self._label(self._team_phrase(ctx), "团队基础")}"] --> B["资源优势\\n{advantage}"]\n'
            '    B --> C["产业协同\\n试制/验证/交付"]\n'
            f'    C --> D["IP 支撑\\n{ip}"]\n'
            '    D --> E["商业转化\\n示范与复制"]'
        )
        return self.mermaid_chart("团队与资源协同图", mermaid)

    def _chart_bp_ch6_6_5(self, ctx: ChapterWriterContext):
        """
        【图表占位】6.5 竞争优势（产品+用户视角）
        slug=bp_ch6_6_5（与正文 bp_module_text 相同）
        建议 chart_type: table  writer_hint: 双视角竞品

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        landscape = self._competitive_points(ctx, limit=2)
        rows = [
            ["产品能力", self._advantages_phrase(ctx, 2), self._join_or_default(landscape[:1], "【待验证】"), "【推断】"],
            ["用户价值", self._team_phrase(ctx), self._join_or_default(landscape[1:2], "【待验证】"), "【推断】"],
        ]
        return self.table_chart("竞争优势双视角对比", ["视角", "本项目优势", "竞品或行业现状", "证据状态"], rows)

    # ------------------------------------------------------------------
    # 正文私有方法与通用辅助函数
    # ------------------------------------------------------------------
    def _write_bp_ch6_6_1(self, ctx: ChapterWriterContext) -> str:
        return self._compose_module(
            ctx,
            f"【事实】核心团队应围绕{self._team_phrase(ctx)}形成“技术研发 + 产业化交付 + 商务拓展”的基本分工，重点突出与成果转化直接相关的经验与资源整合能力。",
            "【待验证】如材料未明确成员姓名、职务与履历，建议仅概括团队结构，不补写具体个人头衔或过往业绩数据。",
        )

    def _write_bp_ch6_6_2(self, ctx: ChapterWriterContext) -> str:
        return self._compose_module(
            ctx,
            "【事实】顾问团队宜补足项目在产业认知、行业渠道、政策理解和商业化节奏控制上的短板，承担资源引荐、关键决策评估和外部背书功能。",
            "【待验证】当前材料若未列明顾问名单、单位和合作方式，应预留顾问方向而非虚构具体专家配置。",
        )

    def _write_bp_ch6_6_3(self, ctx: ChapterWriterContext) -> str:
        return self._compose_module(
            ctx,
            f"【事实】资源优势主要体现在{self._advantages_phrase(ctx, 3)}，这些条件有助于缩短从研发样机到场景验证再到标准化交付的推进周期。",
            f"【推断】若能进一步与{self._team_phrase(ctx)}形成稳定协同，项目在试点获取、交付复制和客户信任建立方面将更具持续性。",
        )

    def _write_bp_ch6_6_4(self, ctx: ChapterWriterContext) -> str:
        return self._compose_module(
            ctx,
            f"【事实】组织侧 IP 布局应围绕{self._ip_phrase(ctx, 3)}展开，重点体现专利、软著、标准或 know-how 在团队分工与商业推进中的保护作用，而非重复技术机理本身。",
            "【推断】建议将核心专利用于锁定关键模块和交付接口，将外围布局用于支撑合作谈判、授权转化和后续产品线延展。",
        )

    def _write_bp_ch6_6_5(self, ctx: ChapterWriterContext) -> str:
        return self._compose_module(
            ctx,
            f"【事实】从产品视角看，本项目优势集中在{self._advantages_phrase(ctx, 2)}；从用户视角看，更重要的是能否在交付效率、效果稳定性和服务响应上形成优于替代方案的综合体验。",
            f"【推断】结合{self._competitive_phrase(ctx, 2)}来看，后续应继续强化差异化证据、标杆案例和复购机制，以扩大竞争壁垒。",
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

    def _team_points(self, ctx: ChapterWriterContext, limit: int = 3) -> list[str]:
        return self._analysis_points(ctx, "team_and_resources", limit)

    def _competitive_points(self, ctx: ChapterWriterContext, limit: int = 2) -> list[str]:
        return self._analysis_points(ctx, "competitive_landscape", limit)

    def _team_phrase(self, ctx: ChapterWriterContext) -> str:
        return self._join_or_default(self._team_points(ctx, limit=2), "团队能力")

    def _advantages_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        return self._join_or_default(self._analysis_points(ctx, "advantages", limit), "资源与能力优势")

    def _ip_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        ip_points = self._analysis_points(ctx, "ip_status", limit)
        if ip_points == ["【待验证】"]:
            return "专利、软著与技术秘密"
        return self._join_or_default(ip_points, "专利、软著与技术秘密")

    def _competitive_phrase(self, ctx: ChapterWriterContext, limit: int) -> str:
        return self._join_or_default(self._competitive_points(ctx, limit), "行业替代方案仍需进一步核验")

    def _join_or_default(self, items: list[str], fallback: str) -> str:
        cleaned = [self._truncate(item, 22) for item in items if self._clean(item) and not self._clean(item).startswith("【待验证】")]
        if not cleaned:
            return fallback
        return "、".join(cleaned)

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
                "role",
                "resource",
                "advantage",
                "status",
            )
            preferred_nested_keys = (
                "items",
                "list",
                "points",
                "members",
                "resources",
                "advantages",
                "patents",
                "landscape",
                "competitors",
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
