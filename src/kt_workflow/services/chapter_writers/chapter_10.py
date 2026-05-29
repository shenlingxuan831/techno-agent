"""中游章节 Writer — 第十章 — 附录 A～F

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_10`，在流水线中的位置：

  … → kt_structure → **kt_chapter_10** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写「附录清单」：把正文放不下的材料条目列出来。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 6 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 0 个），还要返回图表 JSON

你要写的具体内容：6 个附录模块（A～F），清单/索引式，无硬字数上限。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · 一般不需要 LLM 长文；列出「应附哪些材料、是否已有」。
  · 材料没有写「待补充」；可从 extracted_text 摘可附录的实验/IP 线索。

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
#   - extracted_text 摘录
#   - profile.analysis.analysis 中可附录化事实
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
#   - bp_ch10_appx_A | ref=附录A | chart=否 | 技术实验报告与测试数据
#   - bp_ch10_appx_B | ref=附录B | chart=否 | 知识产权证书
#   - bp_ch10_appx_C | ref=附录C | chart=否 | 团队成员履历与资质
#   - bp_ch10_appx_D | ref=附录D | chart=否 | 市场调研与行业报告
#   - bp_ch10_appx_E | ref=附录E | chart=否 | 合作意向书与协议模板
#   - bp_ch10_appx_F | ref=附录F | chart=否 | 财务测算明细与假设

字数/篇幅：清单式，无硬上限
话术模板：templates.md §十
注册表  ：config/bp_transform_outline_registry.json（chapter=10）
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


class Chapter10Writer(BaseChapterWriter):
    """chapter=10 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 10
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

        writers = {
            "bp_ch10_appx_A": self._write_bp_ch10_appx_A,
            "bp_ch10_appx_B": self._write_bp_ch10_appx_B,
            "bp_ch10_appx_C": self._write_bp_ch10_appx_C,
            "bp_ch10_appx_D": self._write_bp_ch10_appx_D,
            "bp_ch10_appx_E": self._write_bp_ch10_appx_E,
            "bp_ch10_appx_F": self._write_bp_ch10_appx_F,
        }
        if module_id in writers:
            return writers[module_id](ctx)

        # 未实现的模块仍返回占位（方便联调；全部实现后可删）
        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext):
        """本章无 needs_chart 模块。"""
        return None

    # ------------------------------------------------------------------
    # 正文私有方法示例（每个模块一个）：
    #
    # def _write_bp_ch10_appx_A(self, ctx: ChapterWriterContext) -> str:
    #     """写 技术实验报告与测试数据 小节。"""
    #     heading = self.module_heading(ctx)
    #     summary = self.analysis_field(ctx, "summary")
    #     return f"{heading}\n\n{summary}\n"
    #
    # 图表私有方法见上方 _chart_* （与 needs_chart 模块一一对应）
    # ------------------------------------------------------------------

    def _write_bp_ch10_appx_A(self, ctx: ChapterWriterContext) -> str:
        """写 附录A 技术实验报告与测试数据。"""
        rows = [
            ["实验/测试报告", self._evidence(ctx, "trl_rationale", "TRL 或验证依据"), "待归档", "支撑技术成熟度、性能指标和可行性结论"],
            ["关键参数与检测数据", self._evidence(ctx, "innovation_detail", "创新性或参数说明"), "待核验", "支撑核心技术、竞品对比和风险判断"],
            ["中试/试点记录", self._excerpt_hint(ctx, ["中试", "试点", "测试", "验证"]), "待补充", "支撑商业化落地路径"],
        ]
        return self._appendix(ctx, rows, self._gap_note(ctx, ["实验数据", "测试报告", "中试", "试点"]))

    def _write_bp_ch10_appx_B(self, ctx: ChapterWriterContext) -> str:
        """写 附录B 知识产权证书。"""
        rows = [
            ["专利/软著/论文清单", self._evidence(ctx, "ip_status", "知识产权状态"), "待核验", "支撑权属、保护范围和技术壁垒"],
            ["权属与许可文件", "【待补充】需提供申请人/权利人、授权状态、许可边界。", "待补充", "避免后续转化中的权属争议"],
            ["专利布局说明", self._evidence(ctx, "advantages", "技术优势"), "待完善", "连接核心优势与知识产权保护策略"],
        ]
        return self._appendix(ctx, rows, self._gap_note(ctx, ["知识产权", "专利", "软著", "权属"]))

    def _write_bp_ch10_appx_C(self, ctx: ChapterWriterContext) -> str:
        """写 附录C 团队成员履历与资质证明。"""
        rows = [
            ["核心成员履历", self._evidence(ctx, "team_and_resources", "团队与资源"), "待核验", "支撑研发能力、交付能力和组织规划"],
            ["顾问/合作单位资质", self._excerpt_hint(ctx, ["团队", "导师", "实验室", "合作单位", "资质"]), "待补充", "支撑外部资源和转化网络"],
            ["设备与平台证明", self._evidence(ctx, "team_and_resources", "团队与资源"), "待完善", "支撑研发验证和持续迭代能力"],
        ]
        return self._appendix(ctx, rows, self._gap_note(ctx, ["团队", "履历", "资质", "实验室"]))

    def _write_bp_ch10_appx_D(self, ctx: ChapterWriterContext) -> str:
        """写 附录D 市场调研与行业报告。"""
        rows = [
            ["目标市场资料", self._evidence(ctx, "target_market", "目标市场"), "待核验", "支撑市场规模、客户画像和切入场景"],
            ["竞品/替代方案资料", self._evidence(ctx, "competitive_landscape", "竞争格局"), "待补充", "支撑竞争分析和差异化定位"],
            ["政策与产业方向资料", self._evidence(ctx, "policy_fit_hint", "政策方向"), "待补充", "支撑政策适配和申报路径"],
        ]
        return self._appendix(ctx, rows, self._gap_note(ctx, ["市场", "行业报告", "竞品", "政策"]))

    def _write_bp_ch10_appx_E(self, ctx: ChapterWriterContext) -> str:
        """写 附录E 合作意向书与协议模板。"""
        rows = [
            ["合作意向书", self._excerpt_hint(ctx, ["合作", "意向", "客户", "企业", "试点"]), "待补充", "支撑需求真实性和场景落地"],
            ["试点/联合验证协议模板", "【待补充】建议列明验证目标、数据归属、保密义务和成果使用边界。", "待补充", "降低试点推进中的合规和交付风险"],
            ["转化/许可协议要点", self._evidence(ctx, "ip_status", "知识产权状态"), "待完善", "支撑收益分配、权利许可和后续商业合作"],
        ]
        return self._appendix(ctx, rows, self._gap_note(ctx, ["合作", "意向书", "协议", "客户"]))

    def _write_bp_ch10_appx_F(self, ctx: ChapterWriterContext) -> str:
        """写 附录F 财务测算明细与假设依据。"""
        gaps = self._items(ctx, "data_gaps")
        rows = [
            ["成本测算底表", "【待验证】需拆分研发、人力、设备、试点、认证、市场拓展等成本项。", "待补充", "支撑第七章成本与现金流"],
            ["收入与定价假设", "【待验证】需提供产品/服务形态、定价口径、销量或项目数量假设。", "待补充", "支撑盈利模式和回本周期"],
            ["融资与资金用途", "【待验证】未取得依据前不写具体融资额和承诺回报。", "待补充", "支撑资源需求与阶段性计划"],
            ["缺失数据清单", "；".join(gaps[:4]) if gaps else "【待验证】财务相关输入尚未形成结构化材料。", "待完善", "作为后续尽调和访谈问题清单"],
        ]
        return self._appendix(ctx, rows, self._gap_note(ctx, ["财务", "成本", "收入", "融资", "预算"]))

    def _appendix(self, ctx: ChapterWriterContext, rows: list[list[str]], note: str) -> str:
        heading = self.module_heading(ctx)
        table = self._markdown_table(["材料条目", "当前可用依据", "状态", "在 BP 中的用途"], rows)
        return (
            f"{heading}\n\n"
            f"本附录用于归档正文引用但不适合展开叙述的支撑材料。当前版本先形成索引清单，正式提交前应由项目团队补齐原件、编号、日期和来源说明。\n\n"
            f"{table}\n\n"
            f"> {note}\n"
        )

    def _evidence(self, ctx: ChapterWriterContext, key: str, label: str) -> str:
        value = self._field(ctx, key)
        if value:
            return f"【事实/待核验】{value}"
        return f"【待补充】analysis.{key} 暂无{label}，需回到原始材料或访谈中补证。"

    def _excerpt_hint(self, ctx: ChapterWriterContext, keywords: list[str]) -> str:
        text = self._clean(ctx.get("extracted_text"))
        if not text:
            return "【待补充】未读取到可用于附录摘录的原文片段。"
        for kw in keywords:
            pos = text.find(kw)
            if pos >= 0:
                start = max(0, pos - 45)
                end = min(len(text), pos + 95)
                snippet = self._clean(text[start:end])
                return f"【事实/待核验】原文片段：{snippet}"
        return "【待补充】原文中未自动定位到明确线索，需人工补充材料编号和来源。"

    def _gap_note(self, ctx: ChapterWriterContext, keywords: list[str]) -> str:
        gaps = [g for g in self._items(ctx, "data_gaps") if any(k in g for k in keywords)]
        if gaps:
            return "【待验证】与本附录相关的缺失项：" + "；".join(gaps[:4]) + "。"
        return "【待验证】如未提供原件或可复核来源，本附录仅作为待补材料索引，不应替代正式证明文件。"

    def _field(self, ctx: ChapterWriterContext, key: str, default: str = "") -> str:
        return self._clean(self.analysis_field(ctx, key, default))

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
    def _markdown_table(columns: list[str], rows: list[list[str]]) -> str:
        header = "| " + " | ".join(columns) + " |"
        sep = "| " + " | ".join(["---"] * len(columns)) + " |"
        body = []
        for row in rows:
            escaped = [str(cell).replace("|", "｜").replace("\n", "<br>") for cell in row]
            body.append("| " + " | ".join(escaped) + " |")
        return "\n".join([header, sep] + body)

    @staticmethod
    def _clean(value: Any) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        return " ".join(text.split())
