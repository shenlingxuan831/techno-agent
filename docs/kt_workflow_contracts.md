# kt_workflow 团队协作契约

本文约定 **入参、写库、上游数据标准**。分工协作时全员以本文 + `config/` 下 JSON schema 为准；变更 breaking 接口前先同步，并递增 **`registry_version`** 或 **`schema_version`**，在第 13 节登记。

**文档分工**

| 文档 | 读者 |
|------|------|
| 本文 | 全员：流水线、artifact、上游 profile |
| [kt_workflow_chapter_writer_guide.md](kt_workflow_chapter_writer_guide.md) | **中游**：按章生成正文/图表 |
| [bp_research_commercialization_outline.md](bp_research_commercialization_outline.md) | 内容纲领、字数 |
| [bp_research_commercialization_templates.md](bp_research_commercialization_templates.md) | 话术与表格骨架 |

---

## 1. 流水线（当前实现）

顺序定义在 `src/kt_workflow/graph.py`。

```
kt_ingest → kt_extract → kt_analyze → kt_structure
    → kt_chapter_00 … kt_chapter_10
    → kt_aggregate → kt_polish → kt_pdf
```

**当前阶段重点：上游已接 DeepSeek；中游按章脚手架分工；下游输出 HTML 预览（正式 PDF 由负责人另行渲染）。**

| 顺序 | 节点 | 做什么 | 调大模型 | 写库 |
|------|------|--------|----------|------|
| 1 | `kt_ingest` | 创建 project/run；记录用户表单与 `source_uri` | 否 | `source_meta` |
| 2 | `kt_extract` | 读 pdf/docx/pptx/xlsx/txt 等，抽出纯文本 | 否 | `extracted_text` |
| 3 | `kt_analyze` | 用 DeepSeek 分析正文，输出结构化 JSON | **是** | `llm_source_analysis` |
| 4 | `kt_structure` | 合并分析结果 + 规则字段，生成统一档案 | 否 | `structured_profile`（v3） |
| 5 | `kt_chapter_*` | 按注册表写各模块正文（及图表） | 规划：是 | `bp_module_text` / `bp_module_chart` |
| 6 | `kt_aggregate` | 按注册表顺序拼整稿 | 否 | `bp_full_draft` |
| 7 | `kt_polish` | 预览阶段直通整稿 | 否 | `bp_polished` |
| 8 | `kt_pdf` | 生成 HTML 预览 `bp_preview.html` | 否 | `pdf_export` + 磁盘 HTML/MD |

**写库规则**：节点内 `with session_scope()`，通过 `repositories` 写入；业务逻辑在 `services/`。

---

## 2. 为最终 PDF 准备的数据链（写库标准）

一次 `run` 在 SQLite（`var/kt_workflow/databases/<run_id>.sqlite`）里按阶段落库，**下游只读、不重复解析用户文件**。

| 阶段 | artifact_type | slug | 内容 | 谁写入 | 谁读取 |
|------|---------------|------|------|--------|--------|
| 进料 | `source_meta` | `default` | 入参 JSON meta | ingest | 调试 |
| 抽文本 | `extracted_text` | `default` | 材料全文纯文本 | extract | analyze；章节可选 |
| **分析** | **`llm_source_analysis`** | **`default`** | **DeepSeek 分析 JSON** | **analyze** | structure；章节可读 `profile.analysis` |
| **档案** | **`structured_profile`** | **`default`** | **v3 统一上下文 JSON** | **structure** | **所有 chapter_*（主入口）** |
| 模块正文 | `bp_module_text` | **模块 `id`** | 该小节 Markdown | chapter_* | aggregate |
| 模块图表 | `bp_module_chart` | **同模块 `id`** | 图表 JSON spec | chapter_* | aggregate / pdf |
| 整稿 | `bp_full_draft` | `default` | 汇编 Markdown | aggregate | polish |
| 润色稿 | `bp_polished` | `default` | 润色 Markdown | polish | pdf |
| 导出 | `pdf_export` | `default` | 路径与说明 | pdf | HTTP 响应 |

类型常量：`src/kt_workflow/constants.py`（禁止手写魔法字符串）。

**JSON schema 文件**

| 文件 | 说明 |
|------|------|
| `config/kt_analysis_output_schema.json` | `llm_source_analysis` 字段清单 |
| `config/kt_source_analysis_llm_cfg.json` | analyze 节点 prompt 与模型参数 |
| `config/bp_transform_outline_registry.json` | 62 模块 id / chapter / writer_hint |
| `config/kt_chapter_chart_spec_schema.json` | `bp_module_chart` JSON 约定 |

---

## 3. 入参 `KTWorkflowInput`

与 `src/kt_workflow/state.py` 一致。

| 字段 | 说明 |
|------|------|
| `project_name` | 案件显示名 → 进入 `submission` |
| `source_uri` | 材料路径（相对仓库根 / `COZE_WORKSPACE_PATH`） |
| `user_type` | 读者/申报方类型（高校、企业等） |
| `contact_info` | 联系方式 |
| `specific_requirements` | 补充说明 |
| `project_id` / `run_id` | 由框架注入 |

示例：`payloads/payload_kt_workflow.json`。

---

## 4. `structured_profile` v3（中游主读对象）

实现：`services/profile_builder.py`。根键 **勿删**；增字段优先放在 `analysis` 或 `downstream`。

| 路径 | 说明 |
|------|------|
| `schema_version` | 整数，当前 **3** |
| `source.source_uri` | 材料路径 |
| `source.excerpt_char_length` | 全文长度 |
| `source.extractor_profile` | 构建器标识 |
| `submission.project_name` | 入参 |
| `submission.user_type` | 入参 |
| `submission.contact_info` | 入参 |
| `submission.specific_requirements` | 入参 |
| `content.excerpt` | 摘录（有长度上限，供 prompt） |
| `content.keywords_top` | 合并后的关键词 |
| `content.trl_hint` | TRL 提示 |
| `analysis` | **与 `llm_source_analysis` 相同结构的 JSON 对象** |
| `downstream` | 预留：各章可向此追加键值 |

`analysis` 各字段含义见 `config/kt_analysis_output_schema.json`。

**升级**：不兼容变更时 `schema_version` +1，更新本文与 schema 文件。

---

## 5. 大纲注册表

文件：`config/bp_transform_outline_registry.json`（`registry_version: 2`，62 模块 **已冻结 id**）。

| 字段 | 说明 |
|------|------|
| `modules[].id` | 全库唯一 slug；**禁止改名** |
| `modules[].chapter` | 0～10，对应 `kt_chapter_XX` |
| `needs_chart` | `true` 时必须写同 id 的 `bp_module_chart` |
| `writer_hint` | 字数、表格、模型提示 |

人文标准：`docs/bp_research_commercialization_*.md`。

---

## 6. 代码分层

### 6.1 节点 `nodes/`

- 编排：调 `services` + `repositories`，更新 `run` 阶段，返回图状态。
- 一章一文件：`node_chapter_XX.py` → `chapter_runner.kt_chapter_runner(..., chapter=n)`。

### 6.2 服务 `services/`

| 模块 | 职责 |
|------|------|
| `document_parser` / `source_extract` | 多格式 → 纯文本 |
| `source_analyzer` | DeepSeek 分析 → JSON |
| `llm_client` | API 客户端与环境变量 |
| `profile_builder` | 构建 `structured_profile` v3 |
| `chapter_writer_contract` | **中游共用类型与接口约定** |

### 6.3 仓库 `repositories/`

- `artifacts`：读写 `kt_artifacts`
- `bp_modules`：`write_module_text` / `write_module_chart_stub`
- `runs`：阶段与状态

---

## 7. 上游分工（当前优先）

| 任务 | 负责人建议 | 改动文件 |
|------|------------|----------|
| 文件抽取（纯文本） | 1 人 | `document_parser.py`, `source_extract.py` |
| DeepSeek 分析 prompt / 字段 | 1 人 | `kt_source_analysis_llm_cfg.json`, `source_analyzer.py` |
| profile 合并与 schema | 与 analyze 同组 | `profile_builder.py`, `kt_analysis_output_schema.json` |
| 环境变量 | 运维/联调 | `.env`, `env.example` |

**环境变量（analyze）**

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `DEEPSEEK_BASE_URL` | 默认 `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 默认 `deepseek-chat` |
| `KT_ANALYSIS_MOCK_LLM=1` | 跳过真实调用（联调 extract/structure） |

**验收**：`python src/main.py -m kt --json-file payloads/payload_kt_workflow.json` 后，库中存在非空 `extracted_text`、`llm_source_analysis`、`structured_profile`（`analysis` 有内容）。

---

## 8. 中游分工（下一阶段）

各章负责人只做 **`kt_chapter_XX`** 及对应 `services/chapter_writers/`（待建），**必读**：

- [kt_workflow_chapter_writer_guide.md](kt_workflow_chapter_writer_guide.md)

要点：

1. 只读 `structured_profile`（必要时 `extracted_text`）。
2. 写入 `bp_module_text`，slug = 注册表 `id`。
3. `needs_chart=true` 时按 `config/kt_chapter_chart_spec_schema.json` 写 `bp_module_chart`。
4. 遵守 `writer_hint` 与 BP 模板中的证据标注 `【事实】/【推断】/【待验证】`。

---

## 9. 变更流程

1. 说明影响哪些节点/artifact。
2. 注册表结构变 → `registry_version` +1；profile 不兼容 → `schema_version` +1。
3. 更新相关 `config/*.json` schema 与本文。
4. 第 13 节登记。

---

## 10. 相关文件

| 用途 | 路径 |
|------|------|
| 图 | `src/kt_workflow/graph.py` |
| 状态 | `src/kt_workflow/state.py` |
| 常量 | `src/kt_workflow/constants.py` |
| 注册表 | `src/kt_workflow/outline_loader.py` |
| 章节桩 | `nodes/chapters/chapter_runner.py` |
| 环境 | `docs/kt_workflow_setup.md` |
| Coze 协作 | `docs/coze_and_team_collaboration.md` |

---

## 11. 变更记录

| 日期 | 变更 |
|------|------|
| 2026-05-20 | 初版契约 |
| 2026-05-20 | 可读版、分层与流程表 |
| 2026-05-20 | **上游定稿**：`kt_analyze`、`llm_source_analysis`、`structured_profile` v3；新增 schema 文件与章节写手指南链接 |
