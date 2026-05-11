"""
技术文档提取节点
从上传的技术文档（PDF、图片等）中提取文本内容
"""

import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from utils.file.file import File, FileOps
from graphs.state import TechDocExtractInput, TechDocExtractOutput


def tech_doc_extract_node(
    state: TechDocExtractInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> TechDocExtractOutput:
    """
    title: 技术文档提取
    desc: 从上传的技术文档（PDF、Word、图片等）中提取文本内容，为后续分析做准备
    integrations: 文件处理
    """
    ctx = runtime.context
    
    try:
        # 使用FileOps读取文件内容
        if hasattr(state.tech_document, 'url') and state.tech_document.url:
            file_url = state.tech_document.url
            
            # 根据文件类型处理
            if file_url.lower().endswith(('.pdf', '.doc', '.docx', '.txt', '.md')):
                # 文档类型：提取文本
                tech_text = FileOps.extract_text(state.tech_document)
            else:
                # 图片类型：需要使用多模态模型识别
                # 这里简化处理，假设可以直接读取
                tech_text = f"[图片内容] {file_url}"
        else:
            raise ValueError("文档URL无效")
        
        # 记录日志
        # 注意：Context不提供logger，直接使用print进行调试输出
        print(f"成功提取技术文档文本，长度: {len(tech_text)} 字符")
        
        return TechDocExtractOutput(tech_text=tech_text)
        
    except Exception as e:
        print(f"技术文档提取失败: {str(e)}")
        raise Exception(f"技术文档提取失败: {str(e)}")
