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

from kt_workflow.services.chapter_writer_contract import ChapterWriterContext, ModuleChartSpec
from kt_workflow.services.chapter_writers._base import BaseChapterWriter


class Chapter04Writer(BaseChapterWriter):
    """chapter=4 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 4
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

        # ---- 在这里按 module_id 添加分支（写真实正文）----
        # if module_id == "bp_ch4_4_1":
        #     return self._write_bp_ch4_4_1(ctx)

        # 未实现的模块仍返回占位（方便联调；全部实现后可删）
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
        """
        【图表占位】4.1 行业概况（PEST、产业链）
        slug=bp_ch4_4_1（与正文 bp_module_text 相同）
        建议 chart_type: mermaid  writer_hint: ≤400

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        # TODO: 替换为真实 chart spec（与同名 module 的正文内容一致）
        return self.scaffold_module_chart(ctx)

    def _chart_bp_ch4_4_2(self, ctx: ChapterWriterContext):
        """
        【图表占位】4.2 市场规模（TAM/SAM/SOM）
        slug=bp_ch4_4_2（与正文 bp_module_text 相同）
        建议 chart_type: table  writer_hint: ≤300

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        # TODO: 替换为真实 chart spec（与同名 module 的正文内容一致）
        return self.scaffold_module_chart(ctx)

    def _chart_bp_ch4_4_3(self, ctx: ChapterWriterContext):
        """
        【图表占位】4.3 目标客户画像
        slug=bp_ch4_4_3（与正文 bp_module_text 相同）
        建议 chart_type: table  writer_hint: 画像表

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        # TODO: 替换为真实 chart spec（与同名 module 的正文内容一致）
        return self.scaffold_module_chart(ctx)

    def _chart_bp_ch4_4_5(self, ctx: ChapterWriterContext):
        """
        【图表占位】4.5 竞争格局（五力+竞品）
        slug=bp_ch4_4_5（与正文 bp_module_text 相同）
        建议 chart_type: table  writer_hint: ≤500

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{run_id}/charts/xxx.png")
        """
        # TODO: 替换为真实 chart spec（与同名 module 的正文内容一致）
        return self.scaffold_module_chart(ctx)

    # ------------------------------------------------------------------
    # 正文私有方法示例（每个模块一个）：
    #
    # def _write_bp_ch4_4_1(self, ctx: ChapterWriterContext) -> str:
    #     """写 行业概况（PEST、产业链） 小节。"""
    #     heading = self.module_heading(ctx)
    #     summary = self.analysis_field(ctx, "summary")
    #     return f"{heading}\n\n{summary}\n"
    #
    # 图表私有方法见上方 _chart_* （与 needs_chart 模块一一对应）
    # ------------------------------------------------------------------
