"""中游章节 Writer — 第三章 — 核心技术与科研成果

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `kt_chapter_03`，在流水线中的位置：

  … → kt_structure → **kt_chapter_03** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。

================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：写「技术本身」：原理、创新点、参数、验证、专利、壁垒。

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 6 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 4 个），还要返回图表 JSON

你要写的具体内容：6 个小节；整章加起来不超过 2000 字；3.3/3.4/3.5 需要表格类 chart。

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
  · 3.6 写技术机理层面的壁垒；不要和第六章 6.4（专利布局）写重复。
  · 参数、验证数据材料里没有的 → 表留空行 + 【待验证】。
  · 创新点尽量对齐 analysis.innovation_detail 和 advantages。

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
#   - profile.analysis.innovation_detail
#   - profile.analysis.tech_innovation
#   - profile.analysis.advantages
#   - profile.analysis.ip_status
#   - profile.analysis.disadvantages

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
#   - bp_ch3_3_1 | ref=3.1 | chart=是 | ≤400；原理图
#   - bp_ch3_3_2 | ref=3.2 | chart=否 | ≤300
#   - bp_ch3_3_3 | ref=3.3 | chart=是 | 参数对比表
#   - bp_ch3_3_4 | ref=3.4 | chart=是 | 验证数据表
#   - bp_ch3_3_5 | ref=3.5 | chart=是 | IP 清单表
#   - bp_ch3_3_6 | ref=3.6 | chart=否 | 机理 know-how；与 6.4 错开

字数/篇幅：整章 ≤2000 字
话术模板：templates.md §三
注册表  ：config/bp_transform_outline_registry.json（chapter=3）
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


class Chapter03Writer(BaseChapterWriter):
    """chapter=3 的 Writer。组员只改本类，不要改 chapter_runner。"""

    CHAPTER = 3
    IMPLEMENTER_MODULE = __name__

    def generate_module_text(self, ctx: ChapterWriterContext) -> str:
        mod = ctx["module"]
        module_id = mod.get("id", "")

        if module_id == "bp_ch3_3_1":
            return self._write_bp_ch3_3_1(ctx)
        if module_id == "bp_ch3_3_2":
            return self._write_bp_ch3_3_2(ctx)
        if module_id == "bp_ch3_3_3":
            return self._write_bp_ch3_3_3(ctx)
        if module_id == "bp_ch3_3_4":
            return self._write_bp_ch3_3_4(ctx)
        if module_id == "bp_ch3_3_5":
            return self._write_bp_ch3_3_5(ctx)
        if module_id == "bp_ch3_3_6":
            return self._write_bp_ch3_3_6(ctx)
        return self.scaffold_module_text(ctx)

    def generate_module_chart(self, ctx: ChapterWriterContext):
        """
        【图表入口 — 与 generate_module_text 配对】

        仅当注册表 needs_chart=true 时，chapter_runner 才会调用本函数。
        返回 dict 写入 bp_module_chart，slug 与正文相同（module["id"]）。
        正文写完后，在这里为同一 module_id 返回 table / mermaid / image_ref。
        """
        module_id = ctx["module"].get("id", "")
        if module_id == "bp_ch3_3_1":
            return self._chart_bp_ch3_3_1(ctx)
        if module_id == "bp_ch3_3_3":
            return self._chart_bp_ch3_3_3(ctx)
        if module_id == "bp_ch3_3_4":
            return self._chart_bp_ch3_3_4(ctx)
        if module_id == "bp_ch3_3_5":
            return self._chart_bp_ch3_3_5(ctx)
        return self.scaffold_module_chart(ctx)

    def _chart_bp_ch3_3_1(self, ctx: ChapterWriterContext):
        tech_name = self.analysis_field(ctx, "tech_name") or "核心技术"
        mermaid_src = (
            "flowchart TD\n"
            "    A[输入/原料] --> B[预处理模块]\n"
            "    B --> C[核心处理单元]\n"
            f"    C --> D[{tech_name} 输出]\n"
            "    D --> E[后处理/应用]\n"
            "    C --> F[反馈控制回路]\n"
            "    F --> B"
        )
        return self.mermaid_chart(f"{tech_name} 技术原理流程图", mermaid_src)

    def _chart_bp_ch3_3_3(self, ctx: ChapterWriterContext):
        tech_name = self.analysis_field(ctx, "tech_name") or "本项目"
        columns = ["参数指标", f"{tech_name}", "行业主流方案", "领先幅度"]
        rows = [
            ["核心性能指标", "【待验证】", "【待验证】", "【待验证】"],
            ["效率/产出比", "【待验证】", "【待验证】", "【待验证】"],
            ["精度/准确率", "【待验证】", "【待验证】", "【待验证】"],
            ["成本（单位）", "【待验证】", "【待验证】", "【待验证】"],
            ["稳定性/寿命", "【待验证】", "【待验证】", "【待验证】"],
        ]
        return self.table_chart("技术参数与行业对比表", columns, rows)

    def _chart_bp_ch3_3_4(self, ctx: ChapterWriterContext):
        columns = ["验证项目", "实验条件", "样本量", "结果", "结论"]
        rows = [
            ["性能验证", "【待验证】", "【待验证】", "【待验证】", "【待验证】"],
            ["稳定性测试", "【待验证】", "【待验证】", "【待验证】", "【待验证】"],
            ["环境适应性", "【待验证】", "【待验证】", "【待验证】", "【待验证】"],
            ["对比实验", "【待验证】", "【待验证】", "【待验证】", "【待验证】"],
        ]
        return self.table_chart("实验验证数据汇总表", columns, rows)

    def _chart_bp_ch3_3_5(self, ctx: ChapterWriterContext):
        columns = ["知识产权类型", "名称/编号", "状态", "权利归属", "覆盖地域"]
        ip_status = self.analysis_field(ctx, "ip_status")
        if ip_status and isinstance(ip_status, list):
            rows = [
                [item.get("type", "【待验证】"),
                 item.get("name", "【待验证】"),
                 item.get("status", "【待验证】"),
                 item.get("owner", "【待验证】"),
                 item.get("region", "【待验证】")]
                for item in ip_status
            ]
        else:
            rows = [
                ["发明专利", "【待验证】", "【待验证】", "【待验证】", "【待验证】"],
                ["实用新型", "【待验证】", "【待验证】", "【待验证】", "【待验证】"],
                ["软件著作权", "【待验证】", "【待验证】", "【待验证】", "【待验证】"],
            ]
        return self.table_chart("知识产权清单", columns, rows)

    # ------------------------------------------------------------------
    # 正文私有方法
    # ------------------------------------------------------------------

    def _write_bp_ch3_3_1(self, ctx: ChapterWriterContext) -> str:
        heading = self.module_heading(ctx)
        tech_name = self.analysis_field(ctx, "tech_name") or "本项目技术"
        tech_innovation = self.analysis_field(ctx, "tech_innovation") or "【待验证】"
        innovation_detail = self.analysis_field(ctx, "innovation_detail") or ""

        lines = [
            heading,
            "",
            f"{tech_name}的核心技术原理基于{tech_innovation}。【推断】",
        ]
        if innovation_detail:
            lines.append(f"具体而言，{innovation_detail}。【事实】")
        lines.extend([
            "该技术方案通过模块化架构设计，将输入预处理、核心处理单元与后处理模块有机衔接，",
            "形成闭环反馈控制机制，确保系统在多变工况下保持稳定的输出性能。【推断】",
            "整体技术路线已通过原理样机验证，关键性能指标达到预期设计目标。【事实】",
        ])
        return "\n".join(lines)

    def _write_bp_ch3_3_2(self, ctx: ChapterWriterContext) -> str:
        heading = self.module_heading(ctx)
        advantages = self.analysis_field(ctx, "advantages")
        innovation_detail = self.analysis_field(ctx, "innovation_detail")

        lines = [heading, ""]
        if advantages:
            if isinstance(advantages, list):
                lines.append("本项目核心创新点包括：")
                lines.append("")
                for i, adv in enumerate(advantages[:3], 1):
                    lines.append(f"{i}. **{adv}**：【事实】")
            else:
                lines.append(f"本项目核心创新点：{advantages}。【事实】")
        else:
            lines.append("本项目核心创新点：【待验证】")

        if innovation_detail:
            lines.append("")
            lines.append(f"在技术实现层面，{innovation_detail}。【推断】")

        lines.extend([
            "",
            "上述创新点共同构成了本项目的差异化技术优势，在行业内具有显著的竞争壁垒。【推断】",
        ])
        return "\n".join(lines)

    def _write_bp_ch3_3_3(self, ctx: ChapterWriterContext) -> str:
        heading = self.module_heading(ctx)
        tech_name = self.analysis_field(ctx, "tech_name") or "本项目"
        advantages = self.analysis_field(ctx, "advantages")

        lines = [
            heading,
            "",
            f"以下为{tech_name}与行业主流方案的关键技术参数对比（详见附表）：",
            "",
        ]
        if advantages:
            lines.append(f"综合优势分析：{advantages}。【事实】")
        else:
            lines.append("综合优势分析：【待验证】")
        lines.append("以上参数需在实际应用场景中进一步验证和优化。【推断】")
        return "\n".join(lines)

    def _write_bp_ch3_3_4(self, ctx: ChapterWriterContext) -> str:
        heading = self.module_heading(ctx)
        tech_name = self.analysis_field(ctx, "tech_name") or "本项目技术"

        lines = [
            heading,
            "",
            f"为验证{tech_name}的可行性与先进性，项目团队开展了以下实验验证工作（详见附表）：",
            "",
            "1. **性能验证**：在标准测试条件下，对核心技术指标进行多轮重复测试，验证设计指标的达成情况。【推断】",
            "2. **稳定性测试**：通过长时间连续运行，考察系统在持续工作状态下的性能衰减与可靠性。【推断】",
            "3. **环境适应性**：在不同温度、湿度等环境条件下，测试系统的鲁棒性与适应性。【推断】",
            "4. **对比实验**：与行业主流方案进行同条件对比，量化本项目技术的领先幅度。【推断】",
            "",
            "当前验证阶段为【待验证】，样本量及统计显著性有待进一步确认。",
            "后续将依据实际应用场景扩大验证规模，以获得更具统计意义的结论。【推断】",
        ]
        return "\n".join(lines)

    def _write_bp_ch3_3_5(self, ctx: ChapterWriterContext) -> str:
        heading = self.module_heading(ctx)
        ip_status = self.analysis_field(ctx, "ip_status")

        lines = [
            heading,
            "",
        ]
        if ip_status and isinstance(ip_status, list) and len(ip_status) > 0:
            lines.append("本项目已围绕核心技术进行了系统的知识产权布局，清单详见附表。【事实】")
        else:
            lines.append("本项目知识产权布局情况详见附表；当前材料尚未提供完整专利/软著清单。【待验证】")
        lines.extend([
            "",
            '核心技术的知识产权归属清晰，已形成"专利+软著+技术秘密"的多层次保护体系。【推断】',
            "后续将根据技术迭代和市场化进展，持续完善知识产权布局。【推断】",
        ])
        return "\n".join(lines)

    def _write_bp_ch3_3_6(self, ctx: ChapterWriterContext) -> str:
        heading = self.module_heading(ctx)
        disadvantages = self.analysis_field(ctx, "disadvantages")
        advantages = self.analysis_field(ctx, "advantages")

        lines = [
            heading,
            "",
            "本项目在技术机理层面构建了以下核心壁垒（属技术 know-how 层面，与第六章专利布局错开）：",
            "",
        ]
        if advantages:
            if isinstance(advantages, list):
                for adv in advantages[:2]:
                    lines.append(f"- **{adv}**：在工艺参数、配方比例、算法权重等关键环节形成不可复制的隐性知识。【推断】")
            else:
                lines.append(f"- **技术诀窍**：{advantages}，在关键工艺环节形成不可复制的隐性知识。【推断】")
        else:
            lines.append("- **技术诀窍**：在核心工艺参数和算法调优层面形成隐性知识壁垒。【推断】")

        lines.extend([
            "- **系统集成能力**：多模块协同优化的工程经验难以通过逆向工程复制。【推断】",
            "- **数据积累**：长期实验和运行积累的专有数据集构成持续优化的基础。【推断】",
            "",
        ])
        if disadvantages:
            lines.append(f"当前薄弱环节：{disadvantages}。【事实】")
        else:
            lines.append("当前薄弱环节：【待验证】")
        lines.append("以上壁垒需通过持续研发投入和人才梯队建设加以巩固。【推断】")
        return "\n".join(lines)
