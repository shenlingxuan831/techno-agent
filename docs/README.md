# 文档索引

| 文档 | 用途 |
|------|------|
| [REPOSITORY_LAYOUT.md](../REPOSITORY_LAYOUT.md) | 仓库目录说明（源码与配置分层） |
| [bp_research_commercialization_outline.md](bp_research_commercialization_outline.md) | 科研商业化 BP 纲领（原则、目录、字数、编审） |
| [bp_research_commercialization_templates.md](bp_research_commercialization_templates.md) | 话术与表格骨架 |
| [kt_workflow_contracts.md](kt_workflow_contracts.md) | **上游契约**：流水线、artifact、profile v3、analyze |
| [kt_workflow_chapter_writer_guide.md](kt_workflow_chapter_writer_guide.md) | **中游必读**：按章生成、读库/写库、接口、分章字段映射 |
| [kt_workflow_framework.md](kt_workflow_framework.md) | kt_workflow 代码框架（直白版） |
| [kt_workflow_setup.md](kt_workflow_setup.md) | 数据库、环境变量、本地运行 |
| [coze_and_team_collaboration.md](coze_and_team_collaboration.md) | Coze/Cursor 协作与 HTTP |

**配置 schema（协作标准）**

| 文件 | 说明 |
|------|------|
| `config/bp_transform_outline_registry.json` | 62 模块 id / chapter / writer_hint |
| `config/kt_analysis_output_schema.json` | `llm_source_analysis` 字段 |
| `config/kt_source_analysis_llm_cfg.json` | DeepSeek 分析 prompt |
| `config/kt_chapter_chart_spec_schema.json` | `bp_module_chart` JSON |

示例请求体：`payloads/`。
