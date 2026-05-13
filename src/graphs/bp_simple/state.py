"""简版 BP 工作流状态（与主转化图独立）。"""

from typing import Literal, Optional
from pydantic import BaseModel, Field
from utils.file.file import File


class BPWorkflowInput(BaseModel):
    """简版 BP 入口：成果材料 + 基础联系信息。"""

    tech_document: File = Field(..., description="技术成果相关材料（路径或 URL）")
    user_type: Literal["高校", "企业", "政府", "投资机构"] = Field(
        default="高校", description="读者/客户类型倾向，影响叙述语气"
    )
    contact_info: str = Field(default="", description="联系方式")
    specific_requirements: Optional[str] = Field(
        default="", description="补充说明、已知合作方、目标区域等"
    )


class BPWorkflowState(BPWorkflowInput):
    """图内状态。"""

    tech_text: str = Field(default="", description="提取后的正文")
    bp_markdown: str = Field(default="", description="生成的 BP 全文（Markdown）")
    bp_file_path: str = Field(default="", description="落盘相对工作区路径")


class BPWorkflowOutput(BaseModel):
    """简版 BP 输出。"""

    bp_markdown: str = Field(..., description="商业计划书 Markdown 正文")
    bp_file_path: str = Field(..., description="相对 COZE_WORKSPACE_PATH 的文件路径")
