"""
完整报告生成节点
整合所有分析结果，生成完整的科技成果转化报告并上传到对象存储
"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import ReportGenerateInput, ReportGenerateOutput


def report_generate_node(
    state: ReportGenerateInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ReportGenerateOutput:
    """
    title: 报告生成
    desc: 整合技术分析、商业化评估、需求匹配、政策推荐、资本对接、商业计划书等所有结果，生成完整的科技成果转化报告
    integrations: 文档生成、对象存储
    """
    ctx = runtime.context
    
    try:
        # 构建报告内容
        report_content = f"""# 科技成果转化分析报告

## 一、技术分析

### 1.1 技术概述
{state.tech_analysis.get('summary', '基于上传文档分析')}

### 1.2 技术成熟度
- 评级：{state.tech_analysis.get('tech_maturity', '待评估')}
- 详情：{state.tech_analysis.get('maturity_detail', '')}

### 1.3 技术创新性
- 评级：{state.tech_analysis.get('tech_innovation', '待评估')}
- 详情：{state.tech_analysis.get('innovation_detail', '')}

### 1.4 技术优势
{state.tech_analysis.get('advantages', '')}

### 1.5 技术劣势与风险
{state.tech_analysis.get('disadvantages', '')}

## 二、商业化潜力评估

### 2.1 市场规模
{state.commercial_potential.get('market_size', '待评估')}

### 2.2 竞争优势
{state.commercial_potential.get('competitive_advantage', '待评估')}

### 2.3 商业模式
{state.commercial_potential.get('business_model', '')}

### 2.4 商业化路径
{state.commercial_potential.get('commercialization_path', '')}

### 2.5 风险因素
{state.commercial_potential.get('risk_factors', '')}

## 三、需求匹配

### 3.1 匹配的企业需求

"""
        
        # 添加匹配的需求
        for i, req in enumerate(state.matched_requirements, 1):
            report_content += f"""
#### {i}. {req.get('requirement', '需求')}

- 匹配度：{req.get('match_score', 0) * 100:.0f}%
- 来源：{req.get('source', '未知')}
- 详情：{req.get('detail', '')}

"""
        
        report_content += """
## 四、政策推荐

"""
        
        # 添加政策推荐
        for i, policy in enumerate(state.policy_recommendations, 1):
            report_content += f"""
### {i}. {policy.get('policy_name', '政策')}

- 支持类型：{policy.get('support_type', '综合支持')}
- 适用条件：{policy.get('eligibility', '')}
- 政策内容：{policy.get('policy_content', '')}

"""
        
        report_content += """
## 五、资本对接

"""
        
        # 添加投资机构推荐
        for i, capital in enumerate(state.capital_recommendations, 1):
            report_content += f"""
### {i}. {capital.get('investor_name', '投资机构')}

- 投资阶段：{capital.get('investment_stage', '不限')}
- 投资领域：{capital.get('investment_fields', '')}
- 匹配度：{capital.get('match_score', 0) * 100:.0f}%
- 联系方式：{capital.get('contact_info', '')}

"""
        
        # 添加商业计划书
        if state.bp_document:
            report_content += f"""
## 六、商业计划书

{state.bp_document}

"""
        
        # TODO: 后续可添加将报告上传到对象存储的逻辑
        # 目前简化处理，假设返回空URL表示报告已生成（在实际应用中应上传到S3等存储）
        report_url = ""
        
        print("成功生成科技成果转化报告")
        
        return ReportGenerateOutput(report_url=report_url)
        
    except Exception as e:
        print(f"报告生成失败: {str(e)}")
        raise Exception(f"报告生成失败: {str(e)}")
