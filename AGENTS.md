# 科技成果转化智能体项目

## 项目概述

- **名称**: 科技成果转化智能体
- **功能**: 基于AI大模型，实现科技成果从技术文档分析、商业化评估、需求匹配、政策对接、资本对接到商业计划书生成的全流程智能化服务

### 核心价值

1. **数据驱动降幻觉**: 所有分析与结论基于结构化数据，通过引用溯源确保输出可靠性
2. **全链路智能匹配**: 构建能够同时理解技术、市场、政策与资本的智能系统
3. **人在回路审核**: 在关键决策点引入人工审核，确保结果的专业性与可控性
4. **系统自我迭代**: 通过用户反馈持续优化知识库与匹配模型

### 四类用户

- **高校**: 科研人员上传技术文档，获取商业化潜力评估和BP生成
- **企业**: 获取技术解决方案智能推荐
- **政府**: 获取产业政策与资金支持推荐
- **投资机构**: 获取技术价值评估与投资建议

---

## 节点清单

| 节点名 | 文件位置 | 类型 | 功能描述 | 配置文件 |
|-------|---------|------|---------|---------|
| tech_doc_extract | `nodes/tech_doc_extract_node.py` | task | 技术文档提取 | - |
| tech_analysis | `nodes/tech_analysis_node.py` | agent | 技术深度分析 | `config/tech_analysis_llm_cfg.json` |
| commercial_eval | `nodes/commercial_eval_node.py` | agent | 商业化潜力评估 | `config/commercial_eval_llm_cfg.json` |
| match_requirements | `nodes/match_requirements_node.py` | agent | 需求智能匹配 | `config/match_requirements_llm_cfg.json` |
| policy_search | `nodes/policy_search_node.py` | agent | 政策检索推荐 | `config/policy_search_llm_cfg.json` |
| capital_match | `nodes/capital_match_node.py` | agent | 资本对接匹配 | `config/capital_match_llm_cfg.json` |
| bp_generation | `nodes/bp_generation_node.py` | agent | 商业计划书生成 | `config/bp_generation_llm_cfg.json` |
| report_generate | `nodes/report_generate_node.py` | task | 完整报告生成 | - |

**类型说明**: 
- `task`: 任务节点（文件处理、报告生成等）
- `agent`: 大模型节点（需要调用AI大模型）

---

## 工作流架构

### 执行流程

```
入口 (GraphInput)
  ↓
tech_doc_extract (文档提取)
  ↓
tech_analysis (技术分析 - Agent)
  ↓
commercial_eval (商业化评估 - Agent)
  ↓
┌────────────────────────────────────────┐
│         并行执行（4个节点）             │
├────────────┬────────────┬───────────────┤
│ match_     │ policy_    │ capital_      │
│ requirements│ search    │ match         │
│ (需求匹配)   │ (政策检索)  │ (资本对接)    │
├────────────┴────────────┴───────────────┤
│           bp_generation (BP生成)          │
└────────────────────────────────────────┘
  ↓
report_generate (报告生成)
  ↓
END (GraphOutput)
```

### 并行执行说明

- `match_requirements`, `policy_search`, `capital_match`, `bp_generation` 四个节点**并行执行**
- 充分利用系统资源，提高处理效率
- 报告生成节点等待所有并行任务完成后汇总结果

---

## 技能使用

本项目主要使用以下技能：

### 大语言模型 (LLM)

- **模型**: doubao-seed-2-0-pro-260215
- **用途**: 所有Agent节点的技术分析、商业评估、匹配推荐、BP生成
- **配置**: 各节点独立的JSON配置文件

### 文件处理

- **工具**: FileOps (来自 utils.file.file)
- **用途**: 读取PDF、Word、图片等技术文档
- **支持格式**: PDF, DOC, DOCX, TXT, MD, PNG, JPG, JPEG等

---

## 数据结构

### GraphInput (工作流输入)

```python
{
    "tech_document": File,  # 技术文档文件
    "user_type": str,        # 用户类型：高校/企业/政府/投资机构
    "contact_info": str,     # 联系方式
    "specific_requirements": str  # 特殊需求（可选）
}
```

### GraphOutput (工作流输出)

```python
{
    "tech_analysis": dict,           # 技术分析结果
    "commercial_potential": dict,    # 商业化潜力评估
    "matched_requirements": list,    # 匹配的企业需求
    "policy_recommendations": list,  # 推荐的政策
    "capital_recommendations": list, # 推荐的投资机构
    "bp_document": str,              # 商业计划书内容
    "report_url": str                 # 完整报告下载链接
}
```

---

## 状态管理

### GlobalState 字段说明

- **技术相关**: `tech_text`, `tech_analysis`, `tech_maturity`, `tech_innovation`
- **商业化相关**: `commercial_potential`, `market_size`, `competitive_advantage`
- **匹配推荐**: `matched_requirements`, `policy_recommendations`, `capital_recommendations`
- **文档生成**: `bp_document`, `report_url`
- **流程控制**: `current_step`, `error_message`

---

## 使用指南

### 输入准备

1. 准备技术文档（PDF、Word、图片等格式）
2. 确定用户类型
3. 准备联系方式

### 调用示例

```python
from utils.file.file import File

# 准备输入
graph_input = {
    "tech_document": File(url="https://example.com/tech_doc.pdf"),
    "user_type": "高校",
    "contact_info": "contact@example.com",
    "specific_requirements": ""
}

# 执行工作流
result = main_graph.invoke(graph_input)

# 获取输出
print(result["tech_analysis"])
print(result["commercial_potential"])
print(result["bp_document"])
```

---

## 扩展建议

### 短期优化

1. **增加数据验证**: 在文档提取和LLM调用之间增加数据质量检查
2. **错误处理优化**: 增加重试机制和降级策略
3. **性能监控**: 添加执行时间统计和资源使用监控

### 中期扩展

1. **知识库集成**: 接入向量数据库实现语义检索
2. **多模态支持**: 增强对视频、音频等技术文档的支持
3. **实时政策更新**: 接入政策数据库实现实时政策检索

### 长期规划

1. **多Agent协同**: 引入CrewAI或AutoGen实现更复杂的Agent协作
2. **自我迭代**: 建立用户反馈闭环，实现系统的持续优化
3. **全链路自动化**: 打通从技术评估到产业落地的完整闭环

---

## 文件清单

### 核心文件

- `src/graphs/state.py` - 状态定义
- `src/graphs/graph.py` - 主图编排
- `src/graphs/nodes/` - 节点实现目录

### 配置文件

- `config/tech_analysis_llm_cfg.json` - 技术分析配置
- `config/commercial_eval_llm_cfg.json` - 商业化评估配置
- `config/match_requirements_llm_cfg.json` - 需求匹配配置
- `config/policy_search_llm_cfg.json` - 政策检索配置
- `config/capital_match_llm_cfg.json` - 资本对接配置
- `config/bp_generation_llm_cfg.json` - BP生成配置

### 节点实现

- `src/graphs/nodes/tech_doc_extract_node.py` - 文档提取
- `src/graphs/nodes/tech_analysis_node.py` - 技术分析
- `src/graphs/nodes/commercial_eval_node.py` - 商业化评估
- `src/graphs/nodes/match_requirements_node.py` - 需求匹配
- `src/graphs/nodes/policy_search_node.py` - 政策检索
- `src/graphs/nodes/capital_match_node.py` - 资本对接
- `src/graphs/nodes/bp_generation_node.py` - BP生成
- `src/graphs/nodes/report_generate_node.py` - 报告生成
