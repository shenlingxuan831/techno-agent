# 仓库目录说明

面向开发者：**两件事**并行存在——（1）**模块化长流程** `kt_workflow`；（2）**主 LangGraph** `graphs/`（含 `bp_simple` 简版一次生成）。

## 顶层

| 路径 | 说明 |
|------|------|
| `src/main.py` | FastAPI、CLI（`-m flow|node|bp|kt|http`）入口 |
| `src/kt_workflow/` | 科技成果转化模块化流水线（DB 中心、按章写模块、汇总） |
| `src/graphs/` | 主工作流图、`bp_simple`、各分析节点 |
| `src/storage/`、`src/utils/` | 存储、文件工具等（主流程依赖） |
| `config/` | LLM 配置、`bp_transform_outline_registry.json`（模块清单） |
| `payloads/` | HTTP/CLI 示例 JSON（`kt` / `flow` / `bp` / `extract`） |
| `scripts/` | `build_bp_transform_registry.py`、本地运行 shell、`pack.sh` |
| `docs/` | 人文标准、kt_workflow 契约与说明（见 `docs/README.md`） |
| `var/kt_workflow/` | 本地运行产物（SQLite、导出 md/pdf），**gitignore** |
| `demo_tech.txt` | 示例材料路径（配合 `payloads` 内 `source_uri`） |

## 已清理项（避免误用）

- **已删除** `scripts/generate_test_doc.py`：依赖硬编码 Coze 路径、且未纳入 `pyproject` 工作流；若需测试 PDF 请另写脚本落到仓库相对路径。
- **`kt_workflow.paths`** 中未使用的 `kt_logs_dir` 已移除；需要日志目录可自行在 `var/kt_workflow` 下创建。

## `bp_simple` 与模块化大纲

- **简版一次成稿**：`src/graphs/bp_simple/bp_outline.md` 供 `compose` 节点拼入 prompt，**已与科研商业化目录对齐**（粗粒度标题）。
- **细粒度落库**：以 `config/bp_transform_outline_registry.json` 为准，与 `bp_outline.md` 层级一致但拆成更多写作单元。
