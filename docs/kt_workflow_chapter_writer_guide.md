# 中游章节生成指南（组员必读）

> **你负责什么**：把 `kt_chapter_00` … `kt_chapter_10` 里的**桩文字**换成真实 BP 正文（及图表）。  
> **你不负责什么**：解析用户上传文件、跑总分析（上游已写入 `structured_profile`）。  
> **必读配套**：纲领 [bp_research_commercialization_outline.md](bp_research_commercialization_outline.md)、话术 [bp_research_commercialization_templates.md](bp_research_commercialization_templates.md)、契约 [kt_workflow_contracts.md](kt_workflow_contracts.md)。

---

## 1. 五句话上手

1. 每个 BP 小节在注册表里有一个 **`id`**（如 `bp_ch3_3_1`），就是你写库的 **slug**。  
2. 生成前先读 **`structured_profile`**（JSON），重点用 **`analysis`** 和 **`content.excerpt`**。  
3. 写出的 Markdown 存 **`bp_module_text`**；要配图的模块再存 **`bp_module_chart`**（slug 相同）。  
4. 字数、表格要求看注册表 **`writer_hint`** 和纲领里的字数表。  
5. 没有依据的数据标 **`【待验证】`**，不要编造专利号、金额、客户名。

---

## 2. 从数据库读什么

### 2.1 主入口：`structured_profile`

```python
import json
from kt_workflow import constants as C
from kt_workflow.repositories import artifacts as art_repo

raw = art_repo.get_latest_text(session, run_id, C.STRUCTURED_PROFILE, "default")
profile = json.loads(raw)
```

| 路径 | 写章节时怎么用 |
|------|----------------|
| `submission.project_name` | 成果/项目名 |
| `submission.user_type` | 政府评审 / 投资机构 / 合作企业 → 影响语气与 0.2 矩阵 |
| `submission.specific_requirements` | 用户补充要求 |
| `content.excerpt` | 材料摘录（prompt 上下文） |
| `content.keywords_top` | 关键词 |
| `content.trl_hint` | TRL 提示 |
| **`analysis.*`** | **大模型分析结果（各章主要依据）** |

### 2.2 `analysis` 字段一览

与 `config/kt_analysis_output_schema.json` 一致：

| 字段 | 含义 |
|------|------|
| `summary` | 成果概述 |
| `tech_name` | 技术/成果名称 |
| `trl_level` / `trl_rationale` | 成熟度及依据 |
| `tech_innovation` / `innovation_detail` | 创新性 |
| `advantages` / `disadvantages` | 优劣势列表 |
| `application_scenarios` | 应用场景 |
| `target_market` | 目标市场 |
| `competitive_landscape` | 竞争格局 |
| `ip_status` | 知识产权 |
| `team_and_resources` | 团队与资源 |
| `commercialization_barriers` | 产业化障碍 |
| `policy_fit_hint` | 政策方向 |
| `keywords` | 关键词 |
| **`data_gaps`** | **材料缺什么 → 正文里标【待验证】并列出** |

### 2.3 可选：`extracted_text`

仅当 `content.excerpt` 不够、需要引用原文细节时再读。不要重复实现文件解析。

---

## 3. 往数据库写什么

### 3.1 正文 `bp_module_text`

- **artifact_type**：`bp_module_text`  
- **slug**：注册表 **`modules[].id`**（如 `bp_ch1_1_2`）  
- **content_text**：该小节 Markdown  

**正文格式约定**

```markdown
## {ref} {title}

（正文段落…）

| 列1 | 列2 |
|-----|-----|
| …   | …   |

> 【事实】/【推断】/【待验证】…
```

- 第一行必须是 `## {ref} {title}`，与注册表一致，便于 aggregate 拼接。  
- 数据标注：`【事实】` 有材料依据；`【推断】` 合理推论；`【待验证】` 缺材料（可引用 `analysis.data_gaps`）。

**写入代码（统一入口）**

```python
from kt_workflow.repositories import bp_modules

bp_modules.write_module_text(session, run_id, mod, markdown_text)
```

### 3.2 图表 `bp_module_chart`

当注册表 **`needs_chart: true`** 时必须写入。

- **slug**：与正文 **相同** 的模块 `id`  
- **content_text**：JSON 字符串，结构见 `config/kt_chapter_chart_spec_schema.json`

```json
{
  "schema_version": 1,
  "chart_type": "table",
  "title": "技术参数对比",
  "spec": {
    "columns": ["指标", "本项目", "行业标准", "备注"],
    "rows": [["精度", "±0.1%", "±0.5%", "【待验证】"]]
  }
}
```

`chart_type` 取值：`table` | `mermaid` | `image_ref` | `placeholder`（仅开发桩）。

```python
bp_modules.write_module_chart_stub(session, run_id, mod["id"], mod["ref"], spec=chart_dict)
```

---

## 4. 共用代码接口（必须遵守）

类型定义：`src/kt_workflow/services/chapter_writer_contract.py`

```python
class ChapterWriterContext(TypedDict, total=False):
    run_id: str
    profile: StructuredProfile      # structured_profile 解析后的 dict
    extracted_text: str | None
    module: BpModuleSpec            # 注册表当前模块
    document_title: str

def generate_module_text(ctx: ChapterWriterContext) -> str:
    """返回该模块完整 Markdown（含 ## 标题）。"""

def generate_module_chart(ctx: ChapterWriterContext) -> ModuleChartSpec | None:
    """needs_chart 时返回 chart spec dict；否则 None。"""
```

**实现位置（已建脚手架）**

```
src/kt_workflow/services/chapter_writers/
  __init__.py          # get_chapter_writer(chapter)
  _base.py             # BaseChapterWriter 基类与工具
  chapter_00.py … chapter_10.py   # 【组员改这里】每章一个文件
```

`chapter_runner.py` 已接入：读 profile → 调 writer → 写库。**一般不要改** `nodes/chapters/node_chapter_XX.py`。

```python
for mod in modules_for_chapter(chapter):
    ctx = build_context(session, state, mod)
    text = chapter_writer.generate_module_text(ctx)
    bp_modules.write_module_text(session, state.run_id, mod, text)
    if mod.get("needs_chart"):
        chart = chapter_writer.generate_module_chart(ctx)
        if chart:
            bp_modules.write_module_chart_stub(...)
```

每人只改自己章的 `chapter_XX.py`，**入参/出参不变**。

---

## 5. 各章读哪些 `analysis` 字段（对照 BP 模板）

按纲领与模板，生成时 **优先用下表字段**；没有的从 `content.excerpt` 找，仍无则 `【待验证】` + 写入时参考 `data_gaps`。

| chapter | 注册表范围 | 主要读的 `analysis` 字段 | 模板要点 |
|---------|------------|--------------------------|----------|
| **0** | 0.1～0.3 | `submission.user_type`；证据规则见模板 0.3 | 保密/版本/阅读矩阵 |
| **1** | 1.1～1.6 执行摘要六块 | `summary`, `tech_name`, `target_market`, `advantages`, `competitive_landscape`, `disadvantages`, `application_scenarios`；财务常缺 → `data_gaps` | 总字数 **800～1200**；六块各见 `writer_hint` |
| **2** | 2.1～2.4 | `summary`, `trl_level`, `trl_rationale`, `application_scenarios`, `team_and_resources` | 2.1/2.2 各 ≤300 字 |
| **3** | 3.1～3.6 | `innovation_detail`, `advantages`, `ip_status`, `disadvantages`；3.6 偏技术机理 | 整章 ≤2000 字；3.3/3.4/3.5 需表 |
| **4** | 4.1～4.6 | `target_market`, `competitive_landscape`, `application_scenarios`, `policy_fit_hint` | 整章 ≤2000 字；4.2 TAM/SAM/SOM 表 |
| **5** | 5.1.1～5.5.1 | `application_scenarios`, `target_market`, `commercialization_barriers` | **5.1 合计 600～800 字**（四子模块注意总预算） |
| **6** | 6.1～6.5 | `team_and_resources`, `ip_status`；**6.4 偏专利布局**，与 3.6 错开 | 整章 ≤800 字 |
| **7** | 7.1～7.6 | 多为 `data_gaps`；无则全章【待验证】+ 假设表 | 成本/收入/现金流表结构见模板 |
| **8** | 8.1～8.5 | `disadvantages`, `commercialization_barriers` | 8.5 风险矩阵表 |
| **9** | 9.1～9.3 | `summary`, `advantages`, `data_gaps` | 9.1/9.2/9.3 字数见纲领 |
| **10** | 附录 A～F | `extracted_text` / `analysis` 中可附录化的事实 | 清单式，无硬字数上限 |

**阅读对象矩阵（0.2）**：`submission.user_type` 或后续扩展的读者类型决定哪些「可选章」要生成；必选章始终生成。

---

## 6. 模块 id 与执行摘要六块（已冻结）

| id | 标题 | writer_hint 摘要 |
|----|------|------------------|
| `bp_ch1_1_1` | 一句话介绍 | ≤50 字话术模板 |
| `bp_ch1_1_2` | 市场机会 | 行业、规模、CAGR、TAM/SAM/SOM |
| `bp_ch1_1_3` | 核心优势 | ≤3 点，量化对比 |
| `bp_ch1_1_4` | 商业模式 | 盈利、定价、渠道 |
| `bp_ch1_1_5` | 财务要点 | 融资、用途、回本（缺则【待验证】） |
| `bp_ch1_1_6` | 风险与结论 | 1 风险 + 措施 + 可行/谨慎/不可行 |

完整 62 模块：`config/bp_transform_outline_registry.json`。

---

## 7. 认领与提交流程

1. **认领**：在组内登记 `chapter` 数字（0～10）。  
2. **开发**：实现 `services/chapter_writers/chapter_XX.py` + 必要时改 `node_chapter_XX.py` 一行调用。  
3. **自测**：跑完 `-m kt` 后打开 SQLite，检查你章所有 `id` 的 `bp_module_text` 非桩、chart 符合 schema。  
4. **合入**：不改 `profile` 根键、不改他人章 `id`、不改上游 extract/analyze 契约。

**PR 检查清单**

- [ ] slug 与注册表 `id` 一致  
- [ ] 含 `## {ref} {title}` 标题行  
- [ ] 遵守 `writer_hint` 字数  
- [ ] 无依据数据标【待验证】  
- [ ] `needs_chart` 模块有合法 `bp_module_chart` JSON  

---

## 8. 常见问题

**Q：材料里没写财务，第 7 章怎么写？**  
A：用 `analysis.data_gaps` 驱动【待验证】，输出空表骨架 + 假设说明，不要编具体金额。

**Q：3.6 和 6.4 都有「技术壁垒」？**  
A：3.6 写机理与 know-how；6.4 写专利组合与 IP 运营。见纲领编审提示。

**Q：5.1 四个子模块各写一段，字数爆了？**  
A：纲领要求 5.1 **合计** 600～800 字；建议在 chapter_5 内做 shared budget 或合并 prompt。

**Q：能否直接读用户 PDF？**  
A：不能。上游 `extracted_text` / `structured_profile` 已是标准入口。

---

## 9. 相关文件

| 文件 | 用途 |
|------|------|
| `config/bp_transform_outline_registry.json` | 模块 id、chapter、writer_hint |
| `config/kt_chapter_chart_spec_schema.json` | 图表 JSON |
| `config/kt_analysis_output_schema.json` | 上游 analysis 字段 |
| `services/chapter_writer_contract.py` | Python 接口类型 |
| `repositories/bp_modules.py` | 写库函数 |
| `nodes/chapters/chapter_runner.py` | 按章循环（待接入你的 writer） |

---

## 10. 变更记录

| 日期 | 变更 |
|------|------|
| 2026-05-20 | 初版：中游读写字段、接口、分章映射、图表 schema |
