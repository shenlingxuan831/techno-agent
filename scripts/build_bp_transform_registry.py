#!/usr/bin/env python3
"""生成 config/bp_transform_outline_registry.json — 《科研成果商业化项目商业计划书》最小写作单元清单。"""

from __future__ import annotations

import json
from pathlib import Path


def _slug_ref(ref: str) -> str:
    return ref.replace(".", "_").replace("–", "-").replace("附录", "appx_")


def modules() -> list[dict]:
    """每个对象为「独立生成、独立落库」的一节或一子节；needs_chart 表示需要配套图表/版式块。"""
    m: list[dict] = []

    def add(
        ch: int,
        ref: str,
        title: str,
        *,
        needs_chart: bool = False,
        writer_hint: str = "",
    ) -> None:
        mid = f"bp_ch{ch}_{_slug_ref(ref)}"
        row: dict = {
            "id": mid,
            "chapter": ch,
            "ref": ref,
            "title": title,
            "needs_chart": needs_chart,
        }
        if writer_hint:
            row["writer_hint"] = writer_hint
        m.append(row)

    # —— 0 文档说明 ——
    add(0, "0.1", "保密级别、版本号与更新日期", writer_hint="封面三行：保密级别、V主.次.修订、日期 YYYY-MM-DD")
    add(
        0,
        "0.2",
        "阅读对象与章节必选矩阵（政府评审 / 投资机构 / 合作企业）",
        writer_hint="生成前先识别阅读对象，仅输出必选+按需的可选章节",
    )
    add(
        0,
        "0.3",
        "数据标注与来源优先级（页脚引用规则）",
        writer_hint="≤200 字；内部实测>第三方报告>学术文献>行业估算",
    )

    # —— 1 执行摘要（总 800～1200 字，无总图；拆 6 块便于并行与复核）——
    add(1, "1.1", "执行摘要 — 项目一句话介绍", writer_hint="总-分-总；首句结论；一句话模板≤50字")
    add(1, "1.2", "执行摘要 — 市场机会", writer_hint="目标行业、TAM/SAM/SOM 若可知则必写")
    add(1, "1.3", "执行摘要 — 核心优势", writer_hint="对比竞品量化，≤3 点")
    add(1, "1.4", "执行摘要 — 商业模式", writer_hint="产品形态+定价+渠道+合作意向类型")
    add(1, "1.5", "执行摘要 — 财务要点", writer_hint="融资额、用途、3 年营收、回本周期")
    add(1, "1.6", "执行摘要 — 风险与可行性结论", writer_hint="1 个关键风险+措施+可行/谨慎/不可行")

    # —— 2 项目背景与概述 ——
    add(2, "2.1", "研发背景", writer_hint="≤300 字：立项来源、周期、团队规模")
    add(2, "2.2", "成果现状（TRL、里程碑）", writer_hint="≤300 字；含研发→验证→落地里程碑表")
    add(2, "2.3", "商业化定位", writer_hint="赛道、切入场景、价值主张一句话")
    add(
        2,
        "2.4",
        "发展愿景与路线图",
        needs_chart=True,
        writer_hint="短/中/长期量化目标；推荐路线图、TRL 曲线",
    )

    # —— 3 核心技术与科研成果（整章建议≤2000字；按小节控字数）——
    add(3, "3.1", "技术原理", needs_chart=True, writer_hint="≤400；通俗原理+A→B→C；推荐原理示意图")
    add(3, "3.2", "核心创新点（3 点）", writer_hint="≤300；每点：突破+痛点+不可替代性")
    add(3, "3.3", "技术参数与行业对比", needs_chart=True, writer_hint="必用参数对比表")
    add(3, "3.4", "验证数据", needs_chart=True, writer_hint="≤500；必用验证阶段汇总表；数据标【事实/推断/待验证】")
    add(3, "3.5", "知识产权", needs_chart=True, writer_hint="≤300；必用 IP 清单表")
    add(3, "3.6", "技术壁垒", writer_hint="≤300；专利/工艺/人才")

    # —— 4 市场分析 ——
    add(4, "4.1", "行业概况（PEST、产业链）", needs_chart=True, writer_hint="≤400")
    add(4, "4.2", "市场规模（TAM/SAM/SOM）", needs_chart=True, writer_hint="≤300；表+趋势")
    add(4, "4.3", "目标客户画像", needs_chart=True, writer_hint="≤300；必用用户画像表")
    add(4, "4.4", "痛点分析", writer_hint="≤300")
    add(4, "4.5", "竞争格局（五力+竞品）", needs_chart=True, writer_hint="≤500；竞品对比表+可选雷达")
    add(4, "4.6", "市场可行性（钻石模型）", writer_hint="≤300")

    # —— 5 商业化落地方案 ——
    add(5, "5.1.1", "技术应用形态 — 技术/产品介绍", writer_hint="实物/虚拟产品描述+配图位")
    add(5, "5.1.2", "技术应用形态 — 应用场景（2～3 个）")
    add(5, "5.1.3", "技术应用形态 — 当前成熟度 TRL")
    add(5, "5.1.4", "技术应用形态 — 边界条件")
    add(5, "5.2", "商业模式", needs_chart=True, writer_hint="以图为主；利益相关者/场景/虚实/营销择一逻辑")
    add(5, "5.3.1", "盈利模式 — 渠道、场景与预期回报", needs_chart=True, writer_hint="篇首概括图+价值链条")
    add(5, "5.3.2", "盈利模式 — 收费方式")
    add(5, "5.3.3", "盈利模式 — 成本构成")
    add(5, "5.3.4", "盈利模式 — 价值估算依据")
    add(5, "5.3.5", "盈利模式 — 收益与回本测算")
    add(5, "5.4", "产业布局", needs_chart=True, writer_hint="≤400；产业链关键点+图标")
    add(5, "5.5.1", "发展规划 — 实施路径", needs_chart=True, writer_hint="研发→推广；百分比或阶段；流程图")

    # —— 6 运营团队 ——
    add(6, "6.1", "核心团队", needs_chart=True, writer_hint="履历表；头像+数据化业绩")
    add(6, "6.2", "顾问团队")
    add(6, "6.3", "资源优势", needs_chart=True, writer_hint="≤400；组图+页尾可复现数据源")
    add(6, "6.4", "技术壁垒与专利布局", writer_hint="≤300；侧重组织侧与布局")
    add(6, "6.5", "竞争优势（产品+用户视角）", needs_chart=True, writer_hint="竞品分析双视角")

    # —— 7 财务规划 ——
    add(7, "7.1", "成本测算", needs_chart=True, writer_hint="≤400；年度成本表")
    add(7, "7.2", "收入预测", needs_chart=True, writer_hint="≤400（可选）；3～5 年")
    add(7, "7.3", "利润测算", needs_chart=True, writer_hint="≤300")
    add(7, "7.4", "现金流预测", needs_chart=True, writer_hint="≤300")
    add(7, "7.5", "盈亏平衡与敏感性", writer_hint="≤300")
    add(7, "7.6", "融资需求", writer_hint="≤400")

    # —— 8 风险 ——
    add(8, "8.1", "技术风险", writer_hint="≤400")
    add(8, "8.2", "市场风险", writer_hint="≤400")
    add(8, "8.3", "政策风险", writer_hint="≤400")
    add(8, "8.4", "运营风险", writer_hint="≤400")
    add(8, "8.5", "风险应对与风险矩阵", needs_chart=True, writer_hint="≤300；风险矩阵表")

    # —— 9 结论 ——
    add(9, "9.1", "项目可行性结论", writer_hint="≤300")
    add(9, "9.2", "核心价值总结", writer_hint="≤200")
    add(9, "9.3", "未来展望", writer_hint="≤200")

    # —— 10 附录 ——
    add(10, "附录A", "技术实验报告与测试数据")
    add(10, "附录B", "知识产权证书（专利/软著）")
    add(10, "附录C", "团队成员履历与资质证明")
    add(10, "附录D", "市场调研数据与行业报告")
    add(10, "附录E", "合作意向书与协议模板")
    add(10, "附录F", "财务测算明细与假设依据")

    return m


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "config" / "bp_transform_outline_registry.json"
    mods = modules()
    data = {
        "document_title": "科研成果商业化项目商业计划书",
        "outline_spec_md": "docs/bp_research_commercialization_outline.md",
        "outline_templates_md": "docs/bp_research_commercialization_templates.md",
        "registry_version": 2,
        "artifact_conventions": {
            "text": "artifact_type=bp_module_text，slug=模块 id（与 JSON 中 id 一致）",
            "chart": "artifact_type=bp_module_chart，slug=与对应正文相同 id。needs_chart=true 时必须写入图表占位或 spec",
            "writer_hint": "可选字段，供生成器/人审控制字数与必备表格；见各模块 writer_hint",
        },
        "modules": mods,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", out, "modules:", len(mods))


if __name__ == "__main__":
    main()
