# kt_workflow 数据库与运行说明

本模块使用 **独立** 于 Coze 托管 PostgreSQL 的连接串，便于本地 SQLite 与生产 Postgres 切换。

**契约（输入、artifact、分层）**：`docs/kt_workflow_contracts.md`。

## 环境变量

| 变量 | 说明 |
|------|------|
| `KT_WORKFLOW_DATABASE_URL` | 可选。不设则每次运行使用 **独立** SQLite：`var/kt_workflow/databases/<run_id>.sqlite`（`run_id` 与请求上下文一致）。 |
| `KT_WORKFLOW_SQL_ECHO` | 设为 `1` 可打印 SQL（调试）。 |
| `COZE_WORKSPACE_PATH` | 建议设为仓库根；影响 `source_uri` 相对路径解析（读入材料）。 |

## BP 文档与注册表

人文标准：`docs/bp_research_commercialization_outline.md`、`docs/bp_research_commercialization_templates.md`；模块清单 `config/bp_transform_outline_registry.json`（`registry_version`）。

## 本地运行目录（默认已 `.gitignore`）

| 路径 | 内容 |
|------|------|
| `var/kt_workflow/databases/` | 每次运行的 SQLite：`{run_id}.sqlite`；未绑定 run 的兜底为 `kt_workflow.sqlite3`（如直接 import 调 `session_scope`）。 |
| `var/kt_workflow/runs/<run_id>/` | 该次导出的 **`bp_preview.html`**（浏览器预览）、`bp_preview_source.md` 等。 |

## 本地 SQLite（默认）

无需安装 PostgreSQL。每次执行 `-m kt`（或 `POST /run_kt_workflow`）会在 `databases/` 下新建对应 `run_id` 的库文件并 `create_all`。

旧版路径 `data/kt_workflow.db` 已不再使用，可手工删除。

## 生产 PostgreSQL

1. 创建空库，例如 `kt_workflow`。
2. 在 `.env` 中设置（示例）：

   ```env
   KT_WORKFLOW_DATABASE_URL=postgresql+psycopg2://用户:密码@主机:5432/kt_workflow
   ```

3. 首次运行同样会 `create_all`。**团队规模变大后**建议引入 Alembic 迁移（本框架未强制）。

## 运行示例

```powershell
cd <仓库根>
$env:COZE_WORKSPACE_PATH = (Get-Location).Path
$env:PYTHONPATH = "$(Get-Location)\src"
.\.venv\Scripts\python.exe src\main.py -m kt --json-file payloads/payload_kt_workflow.json
```

HTTP 与 CLI 等价：`POST /run_kt_workflow`（Body 与上表 JSON 相同）。协作与环境变量说明见 `docs/coze_and_team_collaboration.md`。

## 扩展节点

1. 在 `src/kt_workflow/nodes/` 新增 `node_xxx.py`，实现 `kt_xxx_node(state, config, runtime) -> dict`。
2. 用 `repositories/artifacts.py` / `runs.py` 读写库，勿在节点里散写 SQL。
3. 修改 `src/kt_workflow/graph.py` 的边；同步更新 `registry.py` 中的 `PIPELINE_NODE_IDS`。
4. BP 细粒度小节以 `config/bp_transform_outline_registry.json` 为准；话术与字数见 `docs/bp_research_commercialization_outline.md`；整体流程见 `docs/kt_workflow_framework.md`。

## 表概览

- `kt_projects`：项目/案件
- `kt_workflow_runs`：一次运行实例
- `kt_artifacts`：版本化产物（文本、JSON、后续 chart/pdf 的 `storage_uri`）
