"""
科技成果转化智能体工作流 - 状态定义
用于管理工作流的全局状态、图输入输出、各节点的独立输入输出
"""

from typing import Literal, Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from utils.file.file import File

# 并行分支节点 id（与 graph.add_node 名称一致），供规划层引用
ALL_PARALLEL_TRACKS: Tuple[str, ...] = (
    "match_requirements",
    "policy_search",
    "capital_match",
    "bp_generation",
)


class GraphInput(BaseModel):
    """工作流输入：用户上传的技术文档和基本信息"""
    tech_document: File = Field(..., description="技术文档（支持PDF、Word、图片等格式）")
    user_type: Literal["高校", "企业", "政府", "投资机构"] = Field(..., description="用户类型")
    contact_info: str = Field(..., description="联系方式")
    specific_requirements: Optional[str] = Field(default="", description="特殊需求说明")
    workflow_tracks: Optional[List[str]] = Field(
        default=None,
        description="显式指定要执行的并行分支 id；为空则按 user_type 与模型规划字段自动取舍",
    )
    min_tech_text_chars: int = Field(
        default=30,
        ge=0,
        description="提取后的技术文本低于该长度则视为未通过质量门，不进入 LLM 分析",
    )


class GraphOutput(BaseModel):
    """工作流输出：科技成果转化的完整分析结果"""
    tech_analysis: dict = Field(..., description="技术分析结果")
    commercial_potential: dict = Field(..., description="商业化潜力评估")
    matched_requirements: List[dict] = Field(default=[], description="匹配的企业需求列表")
    policy_recommendations: List[dict] = Field(default=[], description="推荐的政策支持")
    capital_recommendations: List[dict] = Field(default=[], description="推荐的投资机构")
    bp_document: Optional[str] = Field(default="", description="生成的商业计划书内容")
    report_url: str = Field(default="", description="完整报告的下载链接")


class GlobalState(BaseModel):
    """全局状态：工作流执行过程中的共享数据"""
    tech_document: File = Field(..., description="技术文档")
    user_type: str = Field(default="", description="用户类型")
    contact_info: str = Field(default="", description="联系方式")
    specific_requirements: str = Field(default="", description="特殊需求")
    workflow_tracks: Optional[List[str]] = Field(
        default=None,
        description="与 GraphInput 对齐；由规划节点消费",
    )
    min_tech_text_chars: int = Field(default=30, description="质量门阈值")

    # 规划层：可执行分支 + 解释；供调试与前端展示
    workflow_plan: Dict[str, Any] = Field(default_factory=dict, description="结构化工作流规划")
    enabled_tracks: Optional[List[str]] = Field(
        default=None,
        description="当前运行要实际执行的并行分支；为 None 时各节点按全量处理",
    )

    # 技术分析相关
    tech_text: str = Field(default="", description="提取的技术文档文本内容")
    tech_analysis: dict = Field(default={}, description="技术分析结果")
    tech_maturity: str = Field(default="", description="技术成熟度评级")
    tech_innovation: str = Field(default="", description="技术创新性评级")
    downstream_focus: List[str] = Field(
        default_factory=list,
        description="技术分析给出的下游重点（建议使用并行节点 id，供规划层裁剪）",
    )
    retrieval_queries: List[str] = Field(
        default_factory=list,
        description="建议的检索子查询，供后续政策/知识库等扩展",
    )

    # 商业化评估相关
    commercial_potential: dict = Field(default={}, description="商业化潜力评估结果")
    market_size: str = Field(default="", description="市场规模评估")
    competitive_advantage: str = Field(default="", description="竞争优势分析")
    commercial_next_steps: List[str] = Field(
        default_factory=list,
        description="商业化侧建议的下一阶段动作（机器可读要点）",
    )
    due_diligence_topics: List[str] = Field(
        default_factory=list,
        description="建议的尽调/核验主题，供资本或内控流程扩展",
    )

    # 匹配与推荐相关
    matched_requirements: List[dict] = Field(default=[], description="匹配的企业需求")
    policy_recommendations: List[dict] = Field(default=[], description="政策推荐列表")
    capital_recommendations: List[dict] = Field(default=[], description="投资机构推荐")
    
    # BP生成相关
    bp_document: str = Field(default="", description="商业计划书内容")
    report_url: str = Field(default="", description="完整报告URL")
    
    # 流程控制
    current_step: str = Field(default="", description="当前执行步骤")
    error_message: Optional[str] = Field(default=None, description="错误信息")


# ============================================
# 节点独立输入输出定义
# ============================================

class TechDocExtractInput(BaseModel):
    """技术文档提取节点输入"""
    tech_document: File = Field(..., description="上传的技术文档")


class TechDocExtractOutput(BaseModel):
    """技术文档提取节点输出"""
    tech_text: str = Field(..., description="提取的文档文本内容")


class TechAnalysisInput(BaseModel):
    """技术分析节点输入"""
    tech_text: str = Field(..., description="技术文档文本内容")
    user_type: str = Field(..., description="用户类型")


class TechAnalysisOutput(BaseModel):
    """技术分析节点输出"""
    tech_analysis: dict = Field(..., description="技术分析结果")
    tech_maturity: str = Field(..., description="技术成熟度")
    tech_innovation: str = Field(..., description="技术创新性")
    downstream_focus: List[str] = Field(default_factory=list)
    retrieval_queries: List[str] = Field(default_factory=list)


class CommercialEvalInput(BaseModel):
    """商业化评估节点输入"""
    tech_analysis: dict = Field(..., description="技术分析结果")
    user_type: str = Field(..., description="用户类型")


class CommercialEvalOutput(BaseModel):
    """商业化评估节点输出"""
    commercial_potential: dict = Field(..., description="商业化潜力评估")
    market_size: str = Field(..., description="市场规模")
    competitive_advantage: str = Field(..., description="竞争优势")
    commercial_next_steps: List[str] = Field(default_factory=list)
    due_diligence_topics: List[str] = Field(default_factory=list)


class MatchRequirementsInput(BaseModel):
    """需求匹配节点输入"""
    tech_analysis: dict = Field(..., description="技术分析结果")
    user_type: str = Field(..., description="用户类型")
    enabled_tracks: Optional[List[str]] = Field(
        default=None,
        description="规划层给出的可执行分支；非空且不含本节点 id 时跳过 LLM",
    )


class MatchRequirementsOutput(BaseModel):
    """需求匹配节点输出"""
    matched_requirements: List[dict] = Field(..., description="匹配的需求列表")


class PolicySearchInput(BaseModel):
    """政策检索节点输入"""
    tech_analysis: dict = Field(..., description="技术分析结果")
    user_type: str = Field(..., description="用户类型")
    enabled_tracks: Optional[List[str]] = Field(default=None)


class PolicySearchOutput(BaseModel):
    """政策检索节点输出"""
    policy_recommendations: List[dict] = Field(..., description="政策推荐列表")


class CapitalMatchInput(BaseModel):
    """资本对接节点输入"""
    tech_analysis: dict = Field(..., description="技术分析结果")
    commercial_potential: dict = Field(..., description="商业化潜力")
    enabled_tracks: Optional[List[str]] = Field(default=None)


class CapitalMatchOutput(BaseModel):
    """资本对接节点输出"""
    capital_recommendations: List[dict] = Field(..., description="投资机构推荐")


class BPGenerationInput(BaseModel):
    """BP生成节点输入"""
    tech_analysis: dict = Field(..., description="技术分析结果")
    commercial_potential: dict = Field(..., description="商业化潜力评估")
    user_type: str = Field(..., description="用户类型")
    enabled_tracks: Optional[List[str]] = Field(default=None)


class BPGenerationOutput(BaseModel):
    """BP生成节点输出"""
    bp_document: str = Field(..., description="商业计划书内容")


class ReportGenerateInput(BaseModel):
    """报告生成节点输入"""
    tech_analysis: dict = Field(default_factory=dict, description="技术分析结果")
    commercial_potential: dict = Field(default_factory=dict, description="商业化潜力评估")
    matched_requirements: List[dict] = Field(default_factory=list, description="匹配需求")
    policy_recommendations: List[dict] = Field(default_factory=list, description="政策推荐")
    capital_recommendations: List[dict] = Field(default_factory=list, description="投资机构推荐")
    bp_document: str = Field(default="", description="商业计划书")


class ReportGenerateOutput(BaseModel):
    """报告生成节点输出"""
    report_url: str = Field(..., description="完整报告下载链接")


class QualityGateInput(BaseModel):
    """文档质量门输入"""
    tech_text: str = Field(default="", description="提取后的文本")
    min_tech_text_chars: int = Field(default=30, ge=0)


class QualityGateOutput(BaseModel):
    """写入 workflow_plan.quality_gate"""
    workflow_plan: Dict[str, Any] = Field(default_factory=dict)


class QualityGateFailOutput(BaseModel):
    """质量门失败时补齐最小状态，使报告节点仍可运行"""
    tech_analysis: dict = Field(default_factory=dict)
    commercial_potential: dict = Field(default_factory=dict)
    error_message: str = Field(default="")


class QualityGateFailInput(BaseModel):
    workflow_plan: Dict[str, Any] = Field(default_factory=dict)


class WorkflowPlanInput(BaseModel):
    """并行前规划节点输入"""
    user_type: str = Field(default="")
    specific_requirements: str = Field(default="")
    workflow_tracks: Optional[List[str]] = Field(default=None)
    tech_analysis: dict = Field(default_factory=dict)
    commercial_potential: dict = Field(default_factory=dict)
    downstream_focus: List[str] = Field(default_factory=list)
    commercial_next_steps: List[str] = Field(default_factory=list)
    workflow_plan: Dict[str, Any] = Field(default_factory=dict)


class WorkflowPlanOutput(BaseModel):
    """规划结果：更新 workflow_plan 与 enabled_tracks"""
    workflow_plan: Dict[str, Any] = Field(default_factory=dict)
    enabled_tracks: List[str] = Field(default_factory=list)
