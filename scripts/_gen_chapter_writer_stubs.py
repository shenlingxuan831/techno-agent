"""一次性生成 chapter_00..10 脚手架（已生成后可删本脚本）。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "kt_workflow" / "services" / "chapter_writers"

CHAPTERS = [
    {
        "num": 0,
        "class": "Chapter00Writer",
        "file": "chapter_00.py",
        "graph_node": "kt_chapter_00",
        "title": "第 0 部分 — 文档说明",
        "word_budget": "0.3 节 ≤200 字；其余见 writer_hint",
        "modules": [
            ("bp_ch0_0_1", "0.1", "保密级别、版本号与更新日期", False, "封面三行"),
            ("bp_ch0_0_2", "0.2", "阅读对象与章节必选矩阵", False, "政府/投资/企业矩阵"),
            ("bp_ch0_0_3", "0.3", "数据标注与来源优先级", False, "【事实】【推断】【待验证】"),
        ],
        "analysis_fields": [
            "submission.user_type（阅读对象）",
            "submission.project_name",
            "submission.specific_requirements",
        ],
        "template_ref": "docs/bp_research_commercialization_templates.md §0.1～0.3",
    },
    {
        "num": 1,
        "class": "Chapter01Writer",
        "file": "chapter_01.py",
        "graph_node": "kt_chapter_01",
        "title": "第一章 — 执行摘要",
        "word_budget": "整章合计 800～1200 字（六块拆分）",
        "modules": [
            ("bp_ch1_1_1", "1.1", "项目一句话介绍", False, "≤50 字话术"),
            ("bp_ch1_1_2", "1.2", "市场机会", False, "TAM/SAM/SOM"),
            ("bp_ch1_1_3", "1.3", "核心优势", False, "≤3 点"),
            ("bp_ch1_1_4", "1.4", "商业模式", False, "盈利/定价/渠道"),
            ("bp_ch1_1_5", "1.5", "财务要点", False, "缺则【待验证】"),
            ("bp_ch1_1_6", "1.6", "风险与可行性结论", False, "可行/谨慎/不可行"),
        ],
        "analysis_fields": [
            "summary", "tech_name", "target_market", "advantages",
            "competitive_landscape", "application_scenarios", "disadvantages", "data_gaps",
        ],
        "template_ref": "templates.md §一、执行摘要",
    },
    {
        "num": 2,
        "class": "Chapter02Writer",
        "file": "chapter_02.py",
        "graph_node": "kt_chapter_02",
        "title": "第二章 — 项目背景与概述",
        "word_budget": "2.1/2.2 各 ≤300 字",
        "modules": [
            ("bp_ch2_2_1", "2.1", "研发背景", False, "≤300"),
            ("bp_ch2_2_2", "2.2", "成果现状（TRL、里程碑）", False, "≤300"),
            ("bp_ch2_2_3", "2.3", "商业化定位", False, "价值主张"),
            ("bp_ch2_2_4", "2.4", "发展愿景与路线图", True, "路线图 chart"),
        ],
        "analysis_fields": [
            "summary", "trl_level", "trl_rationale", "application_scenarios", "team_and_resources",
        ],
        "template_ref": "templates.md §二",
    },
    {
        "num": 3,
        "class": "Chapter03Writer",
        "file": "chapter_03.py",
        "graph_node": "kt_chapter_03",
        "title": "第三章 — 核心技术与科研成果",
        "word_budget": "整章 ≤2000 字",
        "modules": [
            ("bp_ch3_3_1", "3.1", "技术原理", True, "≤400；原理图"),
            ("bp_ch3_3_2", "3.2", "核心创新点（3 点）", False, "≤300"),
            ("bp_ch3_3_3", "3.3", "技术参数与行业对比", True, "参数对比表"),
            ("bp_ch3_3_4", "3.4", "验证数据", True, "验证数据表"),
            ("bp_ch3_3_5", "3.5", "知识产权", True, "IP 清单表"),
            ("bp_ch3_3_6", "3.6", "技术壁垒", False, "机理 know-how；与 6.4 错开"),
        ],
        "analysis_fields": [
            "innovation_detail", "tech_innovation", "advantages", "ip_status", "disadvantages",
        ],
        "template_ref": "templates.md §三",
    },
    {
        "num": 4,
        "class": "Chapter04Writer",
        "file": "chapter_04.py",
        "graph_node": "kt_chapter_04",
        "title": "第四章 — 市场分析",
        "word_budget": "整章 ≤2000 字",
        "modules": [
            ("bp_ch4_4_1", "4.1", "行业概况（PEST、产业链）", True, "≤400"),
            ("bp_ch4_4_2", "4.2", "市场规模（TAM/SAM/SOM）", True, "≤300"),
            ("bp_ch4_4_3", "4.3", "目标客户画像", True, "画像表"),
            ("bp_ch4_4_4", "4.4", "痛点分析", False, "≤300"),
            ("bp_ch4_4_5", "4.5", "竞争格局（五力+竞品）", True, "≤500"),
            ("bp_ch4_4_6", "4.6", "市场可行性（钻石模型）", False, "≤300"),
        ],
        "analysis_fields": [
            "target_market", "competitive_landscape", "application_scenarios", "policy_fit_hint",
        ],
        "template_ref": "templates.md §四",
    },
    {
        "num": 5,
        "class": "Chapter05Writer",
        "file": "chapter_05.py",
        "graph_node": "kt_chapter_05",
        "title": "第五章 — 商业化落地方案",
        "word_budget": "5.1.1～5.1.4 合计 600～800 字",
        "modules": [
            ("bp_ch5_5_1_1", "5.1.1", "技术/产品介绍", False, "5.1 子块"),
            ("bp_ch5_5_1_2", "5.1.2", "应用场景（2～3 个）", False, "5.1 子块"),
            ("bp_ch5_5_1_3", "5.1.3", "当前成熟度 TRL", False, "5.1 子块"),
            ("bp_ch5_5_1_4", "5.1.4", "边界条件", False, "5.1 子块"),
            ("bp_ch5_5_2", "5.2", "商业模式", True, "以图为主"),
            ("bp_ch5_5_3_1", "5.3.1", "渠道、场景与预期回报", True, ""),
            ("bp_ch5_5_3_2", "5.3.2", "收费方式", False, ""),
            ("bp_ch5_5_3_3", "5.3.3", "成本构成", False, ""),
            ("bp_ch5_5_3_4", "5.3.4", "价值估算依据", False, ""),
            ("bp_ch5_5_3_5", "5.3.5", "收益与回本测算", False, ""),
            ("bp_ch5_5_4", "5.4", "产业布局", True, "≤400"),
            ("bp_ch5_5_5_1", "5.5.1", "实施路径", True, "流程图"),
        ],
        "analysis_fields": [
            "application_scenarios", "target_market", "commercialization_barriers", "trl_level",
        ],
        "template_ref": "templates.md §五",
    },
    {
        "num": 6,
        "class": "Chapter06Writer",
        "file": "chapter_06.py",
        "graph_node": "kt_chapter_06",
        "title": "第六章 — 运营团队与组织规划",
        "word_budget": "整章 ≤800 字；6.3 ≤400；6.4 ≤300",
        "modules": [
            ("bp_ch6_6_1", "6.1", "核心团队", True, "履历表"),
            ("bp_ch6_6_2", "6.2", "顾问团队", False, ""),
            ("bp_ch6_6_3", "6.3", "资源优势", True, "≤400"),
            ("bp_ch6_6_4", "6.4", "技术壁垒与专利布局", False, "组织侧 IP；非 3.6 重复"),
            ("bp_ch6_6_5", "6.5", "竞争优势（产品+用户视角）", True, "双视角竞品"),
        ],
        "analysis_fields": ["team_and_resources", "ip_status", "advantages", "competitive_landscape"],
        "template_ref": "templates.md §六",
    },
    {
        "num": 7,
        "class": "Chapter07Writer",
        "file": "chapter_07.py",
        "graph_node": "kt_chapter_07",
        "title": "第七章 — 财务规划",
        "word_budget": "各小节见 writer_hint；缺数据全章【待验证】",
        "modules": [
            ("bp_ch7_7_1", "7.1", "成本测算", True, "年度成本表"),
            ("bp_ch7_7_2", "7.2", "收入预测", True, "3～5 年"),
            ("bp_ch7_7_3", "7.3", "利润测算", True, ""),
            ("bp_ch7_7_4", "7.4", "现金流预测", True, ""),
            ("bp_ch7_7_5", "7.5", "盈亏平衡与敏感性", False, ""),
            ("bp_ch7_7_6", "7.6", "融资需求", False, "≤400"),
        ],
        "analysis_fields": ["data_gaps（财务多为待验证）"],
        "template_ref": "templates.md §七",
    },
    {
        "num": 8,
        "class": "Chapter08Writer",
        "file": "chapter_08.py",
        "graph_node": "kt_chapter_08",
        "title": "第八章 — 风险分析与应对",
        "word_budget": "8.1～8.4 各 ≤400；8.5 ≤300",
        "modules": [
            ("bp_ch8_8_1", "8.1", "技术风险", False, ""),
            ("bp_ch8_8_2", "8.2", "市场风险", False, ""),
            ("bp_ch8_8_3", "8.3", "政策风险", False, ""),
            ("bp_ch8_8_4", "8.4", "运营风险", False, ""),
            ("bp_ch8_8_5", "8.5", "风险应对与风险矩阵", True, "风险矩阵表"),
        ],
        "analysis_fields": ["disadvantages", "commercialization_barriers", "policy_fit_hint"],
        "template_ref": "templates.md §八",
    },
    {
        "num": 9,
        "class": "Chapter09Writer",
        "file": "chapter_09.py",
        "graph_node": "kt_chapter_09",
        "title": "第九章 — 结论与展望",
        "word_budget": "9.1 ≤300；9.2/9.3 ≤200",
        "modules": [
            ("bp_ch9_9_1", "9.1", "项目可行性结论", False, ""),
            ("bp_ch9_9_2", "9.2", "核心价值总结", False, ""),
            ("bp_ch9_9_3", "9.3", "未来展望", False, ""),
        ],
        "analysis_fields": ["summary", "advantages", "data_gaps"],
        "template_ref": "templates.md §九",
    },
    {
        "num": 10,
        "class": "Chapter10Writer",
        "file": "chapter_10.py",
        "graph_node": "kt_chapter_10",
        "title": "第十章 — 附录 A～F",
        "word_budget": "清单式，无硬上限",
        "modules": [
            ("bp_ch10_appx_A", "附录A", "技术实验报告与测试数据", False, ""),
            ("bp_ch10_appx_B", "附录B", "知识产权证书", False, ""),
            ("bp_ch10_appx_C", "附录C", "团队成员履历与资质", False, ""),
            ("bp_ch10_appx_D", "附录D", "市场调研与行业报告", False, ""),
            ("bp_ch10_appx_E", "附录E", "合作意向书与协议模板", False, ""),
            ("bp_ch10_appx_F", "附录F", "财务测算明细与假设", False, ""),
        ],
        "analysis_fields": ["extracted_text 摘录", "analysis 中可附录化事实", "data_gaps"],
        "template_ref": "templates.md §十",
    },
]


# 各章「大白话」说明（会写入 chapter_XX.py 文件头注释）
PLAIN_TALK: dict[int, dict[str, str | list[str]]] = {
    0: {
        "one_line": "写 BP 最前面的「封面说明」：保密级别、给谁看、数据怎么标注。",
        "write_what": "共 3 个小节（0.1～0.3），一般是规则/模板文字，不一定需要大模型。",
        "tips": [
            "0.2 要根据 submission.user_type 决定读者是政府、投资还是企业。",
            "0.3 写清楚【事实】【推断】【待验证】三种标注，后面各章都要遵守。",
            "本章篇幅短，可先用手写规则跑通，再考虑是否接 LLM。",
        ],
    },
    1: {
        "one_line": "写「执行摘要」：整份 BP 的电梯演讲，拆成 6 个小块分别生成。",
        "write_what": "6 个模块（1.1～1.6）各写一段；合起来 800～1200 字，注意别写太长。",
        "tips": [
            "素材主要在 profile.analysis：summary、target_market、advantages 等。",
            "1.5 财务材料里往往没有 → 写【待验证】，不要编融资额。",
            "1.1 一句话介绍尽量 ≤50 字，用 tech_name + 场景话术。",
        ],
    },
    2: {
        "one_line": "写「项目从哪来、现在到哪一步、打算往哪走」。",
        "write_what": "4 个小节：研发背景、成果现状、商业定位、发展路线图（2.4 要配图）。",
        "tips": [
            "TRL、里程碑重点看 analysis.trl_level / trl_rationale。",
            "2.4 needs_chart=true：除文字外还要在 generate_module_chart 里给路线图 spec。",
        ],
    },
    3: {
        "one_line": "写「技术本身」：原理、创新点、参数、验证、专利、壁垒。",
        "write_what": "6 个小节；整章加起来不超过 2000 字；3.3/3.4/3.5 需要表格类 chart。",
        "tips": [
            "3.6 写技术机理层面的壁垒；不要和第六章 6.4（专利布局）写重复。",
            "参数、验证数据材料里没有的 → 表留空行 + 【待验证】。",
            "创新点尽量对齐 analysis.innovation_detail 和 advantages。",
        ],
    },
    4: {
        "one_line": "写「市场大环境、规模、客户、竞品」——回答「有没有市场」。",
        "write_what": "6 个小节；整章 ≤2000 字；多个小节要带 chart（TAM 表、画像表、竞品表等）。",
        "tips": [
            "target_market、competitive_landscape 是主素材；数字无来源必须【待验证】。",
            "4.2 TAM/SAM/SOM 用 table_chart 生成表格 spec 最省事。",
        ],
    },
    5: {
        "one_line": "写「怎么卖、怎么赚钱、怎么落地」——商业化方案章，模块最多。",
        "write_what": "12 个小节；其中 5.1.1～5.1.4 四段合计只能 600～800 字，分配字数时注意总预算。",
        "tips": [
            "5.1 四个子模块别各写很长，否则汇编后超标。",
            "5.2、5.3.1、5.4、5.5.1 都要 chart，优先 mermaid 或 table。",
            "场景、TRL 看 application_scenarios、trl_level。",
        ],
    },
    6: {
        "one_line": "写「谁来做、有什么资源、专利和竞品优势」。",
        "write_what": "5 个小节；整章 ≤800 字；6.1/6.3/6.5 需要 chart。",
        "tips": [
            "team_and_resources、ip_status 是主素材；人名职称材料没有就别编。",
            "6.4 侧重组织与专利布局，与 3.6 技术壁垒区分开。",
        ],
    },
    7: {
        "one_line": "写「钱」：成本、收入、利润、现金流、融资——材料缺数很常见。",
        "write_what": "6 个小节；多数要带财务表格 chart；没有真实数字就输出空表骨架 + 【待验证】。",
        "tips": [
            "本章最依赖 analysis.data_gaps：里面会提示缺哪些财务信息。",
            "禁止编造具体金额、估值、融资轮次；可以写「假设见附录 F」。",
            "7.2 收入预测标注为可选，材料不足可整节短写。",
        ],
    },
    8: {
        "one_line": "写「可能出什么问题、怎么应对」。",
        "write_what": "5 个小节：四类风险 + 一张风险矩阵表（8.5）。",
        "tips": [
            "从 analysis.disadvantages、commercialization_barriers 拆成四类风险。",
            "8.5 用 table_chart 做「概率×影响」矩阵。",
        ],
    },
    9: {
        "one_line": "写「收尾三段」：能不能做、价值是什么、以后怎样。",
        "write_what": "3 个小节，字数紧（9.1≤300，9.2/9.3≤200）。",
        "tips": [
            "9.1 可行性结论要和前面风险、TRL 一致，不要自相矛盾。",
            "可大量复用 analysis.summary 和 advantages，但要压缩字数。",
        ],
    },
    10: {
        "one_line": "写「附录清单」：把正文放不下的材料条目列出来。",
        "write_what": "6 个附录模块（A～F），清单/索引式，无硬字数上限。",
        "tips": [
            "一般不需要 LLM 长文；列出「应附哪些材料、是否已有」。",
            "材料没有写「待补充」；可从 extracted_text 摘可附录的实验/IP 线索。",
        ],
    },
}


# 与 _base._SUGGESTED_CHART_TYPE 保持一致（生成 chart 方法注释用）
CHART_TYPE_HINT: dict[str, str] = {
    "bp_ch2_2_4": "mermaid",
    "bp_ch3_3_1": "mermaid",
    "bp_ch3_3_3": "table",
    "bp_ch3_3_4": "table",
    "bp_ch3_3_5": "table",
    "bp_ch4_4_1": "mermaid",
    "bp_ch4_4_2": "table",
    "bp_ch4_4_3": "table",
    "bp_ch4_4_5": "table",
    "bp_ch5_5_2": "mermaid",
    "bp_ch5_5_3_1": "mermaid",
    "bp_ch5_5_4": "mermaid",
    "bp_ch5_5_5_1": "mermaid",
    "bp_ch6_6_1": "table",
    "bp_ch6_6_3": "image_ref",
    "bp_ch6_6_5": "table",
    "bp_ch7_7_1": "table",
    "bp_ch7_7_2": "table",
    "bp_ch7_7_3": "table",
    "bp_ch7_7_4": "table",
    "bp_ch8_8_5": "table",
}


def _chart_modules(ch: dict) -> list[tuple]:
    return [m for m in ch["modules"] if m[3]]


def _render_chart_methods(ch: dict) -> str:
    """生成 generate_module_chart 分支 + _chart_* 占位方法。"""
    chart_mods = _chart_modules(ch)
    if not chart_mods:
        return """
    def generate_module_chart(self, ctx: ChapterWriterContext):
        \"\"\"本章无 needs_chart 模块。\"\"\"
        return None
"""

    branches = "\n".join(
        f'        if module_id == "{mid}":\n            return self._chart_{mid}(ctx)'
        for mid, _ref, _title, _c, _hint in chart_mods
    )

    stubs: list[str] = []
    for mid, ref, title, _c, hint in chart_mods:
        ctype = CHART_TYPE_HINT.get(mid, "table")
        hint_line = f"writer_hint: {hint}" if hint else ""
        stubs.append(f'''
    def _chart_{mid}(self, ctx: ChapterWriterContext):
        """
        【图表占位】{ref} {title}
        slug={mid}（与正文 bp_module_text 相同）
        建议 chart_type: {ctype}  {hint_line}

        实现方式示例：
          - 表格: return self.table_chart("标题", ["列1","列2"], [["【待验证】","…"]])
          - 流程: return self.mermaid_chart("标题", "flowchart LR\\n  A-->B")
          - 图片: return self.image_ref_chart("标题", "var/kt_workflow/runs/{{run_id}}/charts/xxx.png")
        """
        # TODO: 替换为真实 chart spec（与同名 module 的正文内容一致）
        return self.scaffold_module_chart(ctx)
''')

    return f"""
    def generate_module_chart(self, ctx: ChapterWriterContext):
        \"\"\"
        【图表入口 — 与 generate_module_text 配对】

        仅当注册表 needs_chart=true 时，chapter_runner 才会调用本函数。
        返回 dict 写入 bp_module_chart，slug 与正文相同（module["id"]）。
        正文写完后，在这里为同一 module_id 返回 table / mermaid / image_ref。
        \"\"\"
        module_id = ctx["module"].get("id", "")
{branches}
        return self.scaffold_module_chart(ctx)
""" + "".join(stubs)


def _plain_section(ch: dict) -> str:
    plain = PLAIN_TALK.get(ch["num"], {})
    one_line = plain.get("one_line", "")
    write_what = plain.get("write_what", "")
    tips = plain.get("tips") or []
    tips_block = "\n".join(f"  · {t}" for t in tips)
    mod_count = len(ch["modules"])
    chart_count = sum(1 for m in ch["modules"] if m[3])

    return f"""
================================================================================
【大白话：组员先看这里（3 分钟）】
================================================================================
一句话：{one_line}

整个 BP 流水线里，上游同事已经做完这些事：
  · 读了用户上传的材料（extract）
  · 用大模型做了总分析（analyze）
  · 把结果整理成 structured_profile 存进数据库（structure）

轮到你的章节时，程序会自动：
  1. 从数据库读出 profile（里面有 analysis 字典，像「素材包」）
  2. 按注册表把本章拆成 {mod_count} 个小模块，**逐个**调用本文件的 generate_module_text
  3. 你返回一段 Markdown 字符串，程序帮你写入 bp_module_text（不用你手写 SQL）
  4. 若 needs_chart=true（本章共 {chart_count} 个），还要返回图表 JSON

你要写的具体内容：{write_what}

类比：上游是「备菜 + 写菜谱摘要」，你是「按菜谱把这一章的每一道菜炒出来」；
      不需要你自己去买菜（重新读 PDF），也不需要你改菜单结构（注册表 id）。

现在代码里 return 的是 scaffold_module_text（占位），你改完后应变成真实 BP 段落。

本章特别注意：
{tips_block}

怎么算「做完了」？
  · 跑一遍：python src/main.py -m kt --json-file payloads/payload_kt_workflow.json
  · 打开 SQLite，看本章各模块 id 的正文不再是「脚手架占位」字样
  · 字数、表格、chart 是否符合 writer_hint 和 templates.md
"""


def render(ch: dict) -> str:
    mod_lines = "\n".join(
        f"#   - {mid} | ref={ref} | chart={'是' if chart else '否'} | {hint or title}"
        for mid, ref, title, chart, hint in ch["modules"]
    )
    af = "\n".join(f"#   - profile.analysis.{f}" if not f.startswith("submission") and not f.startswith("extracted") else f"#   - profile.{f}" if f.startswith("submission") else f"#   - {f}" for f in ch["analysis_fields"])

    return f'''"""中游章节 Writer — {ch["title"]}

================================================================================
【你在改什么】
================================================================================
本文件对应 LangGraph 节点 `{ch["graph_node"]}`，在流水线中的位置：

  … → kt_structure → **{ch["graph_node"]}** → … → kt_aggregate → …

职责：读取上游已写入数据库的 `structured_profile`，为本章每个最小模块生成
Markdown 正文（及可选图表 JSON），写入 `bp_module_text` / `bp_module_chart`。

**请勿在本文件内**：解析用户上传文件、调用 ingest/extract/analyze、修改 profile 根键名。
{_plain_section(ch)}
================================================================================
【对接接口（必须实现/遵守）】
================================================================================
基类     : kt_workflow.services.chapter_writers._base.BaseChapterWriter
契约类型 : kt_workflow.services.chapter_writer_contract
  - ChapterWriterContext  （chapter_runner 传入的上下文 dict）
  - generate_module_text(ctx) -> str   （Markdown，含 ## {{ref}} {{title}} 首行）
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
{af}

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
  · 本章需实现图表的模块数：{len(_chart_modules(ch))}  → 见下方 _chart_* 方法
  · JSON 规范：config/kt_chapter_chart_spec_schema.json

================================================================================
【本章模块清单（slug = id，勿改）】
================================================================================
{mod_lines}

字数/篇幅：{ch["word_budget"]}
话术模板：{ch["template_ref"]}
注册表  ：config/bp_transform_outline_registry.json（chapter={ch["num"]}）
组员指南：docs/kt_workflow_chapter_writer_guide.md

================================================================================
【实现步骤（建议）】
================================================================================
1. 打开本文件底部的 `generate_module_text`，找到 TODO。
2. 用 `if module_id == "bp_chX_..."` 区分每个小节（id 见上方模块清单）。
3. 从 ctx 取素材：self.analysis_field(ctx, "字段名") 或 self.submission_field(ctx, "字段名")。
4. 拼 Markdown：第一行用 self.module_heading(ctx)，正文按 templates.md 写。
5. 需要大模型时：在本文件或 services/ 新文件写 prompt 函数，这里只负责调用。
6. needs_chart 的小节：在 generate_module_chart 里走 _chart_{{module_id}} 分支。
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
  · 第一行：## {{ref}} {{title}}  （与注册表一致）
  · 正文：人类可读的 BP 段落，不是 JSON
  · 不要 return 整个 profile；只 return **当前这一个模块** 的正文
  · slug 不用你管：程序用 module["id"] 自动存库

================================================================================
"""

from __future__ import annotations

from kt_workflow.services.chapter_writer_contract import ChapterWriterContext, ModuleChartSpec
from kt_workflow.services.chapter_writers._base import BaseChapterWriter


class {ch["class"]}(BaseChapterWriter):
    \"\"\"chapter={ch["num"]} 的 Writer。组员只改本类，不要改 chapter_runner。\"\"\"

    CHAPTER = {ch["num"]}
    IMPLEMENTER_MODULE = __name__

    def generate_module_text(self, ctx: ChapterWriterContext) -> str:
        \"\"\"
        【你要改的核心函数】

        chapter_runner 每处理注册表里的一个模块，就会调用一次本函数。
        ctx["module"] 就是「当前这一小节」的信息（id、标题、writer_hint 等）。
        ctx["profile"] 是上游准备好的 structured_profile（重点用 ["analysis"]）。

        现在：所有模块都走最后的 scaffold_module_text（占位）。
        你要做：用 module_id 分支，分别 return 真实 Markdown 字符串。
        \"\"\"
        mod = ctx["module"]
        module_id = mod.get("id", "")

        # ---- 在这里按 module_id 添加分支（写真实正文）----
        # if module_id == "{ch["modules"][0][0]}":
        #     return self._write_{ch["modules"][0][0]}(ctx)

        # 未实现的模块仍返回占位（方便联调；全部实现后可删）
        return self.scaffold_module_text(ctx)
{_render_chart_methods(ch)}
    # ------------------------------------------------------------------
    # 正文私有方法示例（每个模块一个）：
    #
    # def _write_{ch["modules"][0][0]}(self, ctx: ChapterWriterContext) -> str:
    #     \"\"\"写 {ch["modules"][0][2]} 小节。\"\"\"
    #     heading = self.module_heading(ctx)
    #     summary = self.analysis_field(ctx, "summary")
    #     return f"{{heading}}\\n\\n{{summary}}\\n"
    #
    # 图表私有方法见上方 _chart_* （与 needs_chart 模块一一对应）
    # ------------------------------------------------------------------
'''


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for ch in CHAPTERS:
        path = ROOT / ch["file"]
        path.write_text(render(ch), encoding="utf-8")
        print("wrote", path)


if __name__ == "__main__":
    main()
