- **仓库目录说明**：`REPOSITORY_LAYOUT.md`；**文档索引**：`docs/README.md`。

## 协作与环境

- **Coze / Cursor 共用同一套仓库**：工作区根目录对齐，见 `docs/coze_and_team_collaboration.md`（模型是否必配、HTTP 接口、分工建议）。
- **契约**：`docs/kt_workflow_contracts.md`（`KTWorkflowInput`、artifact slug、`structured_profile` schema）。
- **BP 提纲与话术（科研商业化）**：`docs/bp_research_commercialization_outline.md`、`docs/bp_research_commercialization_templates.md`。
- **kt_workflow 默认产物**：`var/kt_workflow/`（SQLite、按 `run_id` 分目录的导出文件），详见 `docs/kt_workflow_setup.md`。

## 本地运行

### 运行流程

```bash
bash scripts/local_run.sh -m flow
```

### 运行节点

```bash
bash scripts/local_run.sh -m node -n node_name
```

### 科技成果转化模块化流程（CLI）

PowerShell 示例（仓库根目录）：

```powershell
$env:COZE_WORKSPACE_PATH = (Get-Location).Path
$env:PYTHONPATH = "$(Get-Location)\src"
.\.venv\Scripts\python.exe src\main.py -m kt --json-file payloads\payload_kt_workflow.json
```

### 启动 HTTP 服务（含 `POST /run_kt_workflow`）

```bash
bash scripts/http_run.sh -m http -p 5000
```
