# kt_workflow 代码框架（直白版）

这份文档用日常语言说明：**科技成果转化 BP 流水线**在代码里是怎么拆的、数据存在哪、最后怎么拼成一份长文稿。

## 一句话

程序把「跑一趟任务」记在数据库里，每一步往库里**追加**一条产物；细粒度 BP 按**大纲里的最小模块**一块一块写进去，
最后用**汇总节点**按固定顺序读出所有模块，合成一份完整 Markdown，再润色、导出。

## 顶层：从哪里进入

- 入口在 `src/main.py` 的 `run_kt_workflow`（`-m kt` 会走到这里）。
- 图定义在 `src/kt_workflow/graph.py`：节点一条线串起来，没有并行分叉。
- **环境、数据库连接、怎么本地跑一次**见 `docs/kt_workflow_setup.md`（本文不重复环境细节）。
- **冻结契约**（入参、artifact、profile schema）：`docs/kt_workflow_contracts.md`。
- **读源文件**：`src/kt_workflow/text_io.py`（`read_source_text`），供 `services/source_extract` 与节点共用，避免循环导入。

## 图在干什么（节点顺序）

当前顺序可以理解为：

1. **收材料** → **抽文本** → **结构化画像**（前三步把原始输入变成可引用的「库里的标准件」）。
2. **第 0 章到第 10 章**（共 11 个节点：`kt_chapter_00` … `kt_chapter_10`）：每一章节点负责把**该章在注册表里列出的所有最小模块**各写一条正文（需要图的话再写一个图表占位）。
3. **汇总**：按注册表顺序把所有模块正文（和可选图表 JSON）拼成 `bp_full_draft`。
4. **润色**：在整篇草案上套一层语言/格式桩，得到 `bp_polished`。
5. **导出 PDF**（若已实现则是读润色稿或草案落盘）。

与节点名顺序一致的一份清单在 `src/kt_workflow/registry.py` 的 `PIPELINE_NODE_IDS` 里，改图时可以对表检查有没有漏改。

## 「最小模块」从哪来：注册表

- 文件：`config/bp_transform_outline_registry.json`。
- 一般由脚本生成：`scripts/build_bp_transform_registry.py`（改大纲结构时改脚本或 JSON，再运行生成）。
- 代码读取：`src/kt_workflow/outline_loader.py`（`load_registry`、`modules_for_chapter`、`all_modules_in_order`）。

每条模块大致包含：`id`（稳定编号）、`chapter`（第几章）、`ref`（如 1.2）、`title`、`needs_chart`、`writer_hint`（可选）。

**重要约定**：正文和图表在数据库里用**同一个** `slug`，等于模块的 `id`，这样汇编时不会对错行。

## 仓库里默认落盘（与 Git 隔离）

不设 `KT_WORKFLOW_DATABASE_URL`、走 SQLite 时：

- `var/kt_workflow/databases/<run_id>.sqlite`：与该次 `Context.run_id` 对应的库文件（`bind_sqlite_run`）。
- `var/kt_workflow/runs/<run_id>/`：如 **`bp_preview.html`**（双击浏览器预览）、`bp_preview_source.md`。

`var/kt_workflow/` 整体在 `.gitignore` 中。

## 数据存在哪：artifacts 思路

业务上把它想成「一次运行 = 一个文件夹，里面很多版本化文件」：

- 表名等在 `bootstrap`/模型里；产物集中在 **`kt_artifacts`**（具体字段以代码为准）。
- 常用 **artifact_type**（字符串常量）在 `src/kt_workflow/constants.py`，例如：
  - `bp_module_text`：某一小节的 Markdown 正文，`slug` = 模块 `id`。
  - `bp_module_chart`：与上一小节同 `slug`，放图表 spec 或占位 JSON 文本。
  - `bp_full_draft`：汇总后的整篇 Markdown（`slug` 一般用 `default`）。
  - `bp_polished`、`pdf_export`：后处理结果。

写入封装在 `src/kt_workflow/repositories/`。**按模块写正文**的逻辑在 `repositories/bp_modules.py`（`write_module_text`、`write_module_chart_stub`、`get_*`）。

## 章节节点：为什么有 13 个文件

- 目录：`src/kt_workflow/nodes/chapters/`。
- 每个 `node_chapter_XX.py` 只做一件事：调用 `chapter_runner.kt_chapter_runner(..., chapter=X)`。
- **共享实现**在 `chapter_runner.py`：遍历该章所有模块，写桩正文；若 `needs_chart` 为真则再写一条图表占位。

这样拆文件是为了：**以后要按章替换模型、限流、或人工审核**，可以只动某一章的 Python 入口，而不改 runner 核心。

## 汇总节点在做什么

`src/kt_workflow/nodes/node_aggregate.py`：

1. 按 `all_modules_in_order()` 的顺序遍历每个模块 `id`。
2. 取该 `id` 下最新的 `bp_module_text`；若有 `bp_module_chart`，在汇整稿里插一段注释 + JSON 代码块（便于后续替换成真图）。
3. 把整个字符串写入 `bp_full_draft`。

所以：**最终文档顺序 = JSON 注册表里 `modules` 数组顺序**；若你要调整成书顺序，应改注册表生成逻辑，而不是在 aggregate 里手写顺序。

## 改流水线时建议动哪些文件

| 目标 | 去哪改 |
|------|--------|
| 换节点顺序、加减节点 | `graph.py` + `registry.py` |
| 大纲增删小节、改模块 id | `scripts/build_bp_transform_registry.py` 或 JSON，然后重跑脚本 |
| 某一章生成策略（只这一章用不同 prompt） | 对应 `nodes/chapters/node_chapter_XX.py` 或扩展 `chapter_runner` |
| 汇总格式（章节标题、图表占位语法） | `node_aggregate.py` |
| artifact 类型名 | `constants.py` + 所有 `write_artifact` / `get_latest` 调用处 |

## 和「旧版四并行节点」的关系

早期示例是「执行摘要 / 市场 / 图表 / 计算」四个节点并行再汇总；当前主线已改为**按大纲章节顺序写细粒度模块**。
若你在旧文档或输出里看到 `kt_bp_exec_summary` 等名字，那是历史示例，当前 `graph.py` 已不再引用。
