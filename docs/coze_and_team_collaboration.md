# 在 Coze 与 Cursor 之间协作、模型配置与分工说明

本文回答三件事：**别人主要在 Coze 上改/跑时怎么少踩坑**、**大模型要不要配**、**组员怎么分工**（要不要 HTTP 接口）。

---

## 1. 让仓库在 Coze 上也「好处理」

核心原则是：**仓库根目录 = 工作区根**，与本地一致。

| 约定 | 说明 |
|------|------|
| `COZE_WORKSPACE_PATH` | 在 Coze 云开发 / 沙箱里一般会自动指向项目根；本地请显式设为仓库根（与 `docs/kt_workflow_setup.md` 一致）。 |
| 相对路径 | `payloads/payload_kt_workflow.json` 里的 `source_uri`、`config/*.json`、注册表 `config/bp_transform_outline_registry.json` 都相对仓库根解析；**不要假设**只有 Cursor 才有某盘符路径。 |
| Loop 追踪 | 本地不想连 `api.coze.cn` 上报时，在 `.env` 设 `SLX_LOCAL_NO_COZE_LOOP=1`（见 `env.example`）。Coze 线上保持默认即可。 |
| 依赖 | 与 `requirements-windows.txt` / `pyproject.toml` 保持一致；组员改依赖后要更新锁文件或 requirements，避免「我这里能跑」现象。 |

**Cursor 与 Coze 的分工建议**：业务逻辑、节点、注册表脚本在 Git 里协作；Secrets（API Key）只放在各环境变量 / Coze 密钥管理里，不要提交。

---

## 2. 大模型：还要不要配置？能不能直接跑？

要分 **哪条流程**：

### `kt_workflow`（`-m kt` / 模块化科技成果转化流水线）

- **上游**（ingest → extract → **analyze** → structure）已接 **DeepSeek 纯文本分析**，产物写入 `llm_source_analysis` 与 `structured_profile` v3。
- **中游**各章节点当前仍为**桩**；组员按 [kt_workflow_chapter_writer_guide.md](kt_workflow_chapter_writer_guide.md) 接入真实生成。
- 联调图与库、暂不调用 analyze 时可设 `KT_ANALYSIS_MOCK_LLM=1`（见 `env.example`）。
- DeepSeek：`DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`。

### 其它图（主 `flow`、`bp_simple`、`bp`、各分析节点等）

- 默认会通过 `coze_coding_dev_sdk.LLMClient` 调模型，需要 **方舟 / OpenAI 兼容** 的 Key 与 Base URL（见 `env.example`：`ARK_API_KEY`、`OPENAI_BASE_URL` 等）。
- 若暂时无 Key，**简版 BP** 可设 `BP_SIMPLE_MOCK_LLM=1` 走占位输出（见 `env.example` 注释）。

---

## 3. 组员分工协作：需要协议 / 接口吗？

### 必须用 Git 对齐的「契约」

- **入参 JSON**：`kt_workflow` 与 `KTWorkflowInput` 一致，字段见 `src/kt_workflow/state.py`（如 `project_name`, `source_uri`, `user_type`, `contact_info`, `specific_requirements`）。
- **上游写库标准**：`docs/kt_workflow_contracts.md` + `config/kt_analysis_output_schema.json`。
- **中游生成标准**：`docs/kt_workflow_chapter_writer_guide.md` + `config/kt_chapter_chart_spec_schema.json` + `services/chapter_writer_contract.py`。
- **细粒度小节 id**：以 `config/bp_transform_outline_registry.json` 为准；`bp_module_text` / `bp_module_chart` 的 **slug = 模块 `id`**，改大纲要动生成脚本并约定同步。
- **数据库**：不设 `KT_WORKFLOW_DATABASE_URL` 时，每次运行单独 SQLite：`var/kt_workflow/databases/<run_id>.sqlite`（目录已 `.gitignore`）。团队共享跑数则用 Postgres 连接串。

### HTTP 接口（给 Coze 工作流 / 其它服务调）

服务启动后（`python src/main.py -m http -p 5000`，且 `PYTHONPATH` 含 `src`）：

| 路径 | 用途 |
|------|------|
| `POST /run_kt_workflow` | 与 CLI `python ... -m kt --json-file ...` 相同逻辑，Body 为 JSON，与 `payloads/payload_kt_workflow.json` 同形。 |
| `POST /run_bp_simple` | 简版 BP。 |
| `POST /run` | 主 LangGraph 流程。 |

可选请求头：`x-run-id`（与 `/run` 一致，便于追踪；见 `main.py` 中 `HEADER_X_RUN_ID`）。

**不强制**人人都写 HTTP：本地 CLI `-m kt` 与 CI 脚本即可；**需要** Coze 画布里的「HTTP 请求」节点或外部回调时，用 `POST /run_kt_workflow` 最直接。

### 建议的模块分工（示例）

- **上游 A**：`extract` / `analyze` / `structure`（`source_extract`、`source_analyzer`、`profile_builder`）。
- **中游 B～K**：按 `chapter` 0～10 认领，实现 `services/chapter_writers/chapter_XX.py`（见章节写手指南）。
- **大纲 C**：维护 `config/bp_transform_outline_registry.json`（id 已冻结，小改 writer_hint 可 PR）。
- **下游 D**：`aggregate` / `polish` / `pdf`（当前阶段可后置）。
- **联调 E**：`main.py` HTTP、`.env` 示例、文档索引。

---

## 相关文档

- 数据库与环境：`docs/kt_workflow_setup.md`
- 代码框架白话说明：`docs/kt_workflow_framework.md`
- **上游契约**：`docs/kt_workflow_contracts.md`
- **中游章节生成**：`docs/kt_workflow_chapter_writer_guide.md`
