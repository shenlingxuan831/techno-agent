#!/usr/bin/env python3
"""
生成测试用的技术文档
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os

def create_test_pdf():
    """创建一个测试用的技术文档PDF"""
    output_path = "/workspace/projects/assets/mock/test_tech_doc.pdf"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # 标题
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50*mm, height - 50*mm, "人工智能芯片技术白皮书")
    
    # 内容
    c.setFont("Helvetica", 12)
    y_position = height - 80*mm
    
    sections = [
        ("摘要", 
         "本文档介绍了一种基于新型神经网络架构的人工智能芯片技术。"
         "该技术采用存算一体架构，在提升算力的同时大幅降低能耗。"
         "核心技术包括：稀疏化计算、动态电压频率调节、近存计算等。"),
        
        ("技术特点", 
         "1. 高能效比：相比传统GPU，能效提升10倍以上\n"
         "2. 低延迟：端到端推理延迟小于10ms\n"
         "3. 可编程性：支持多种神经网络架构\n"
         "4. 小型化：芯片面积小于50平方毫米"),
        
        ("应用场景",
         "- 边缘计算设备\n"
         "- 智能安防监控\n"
         "- 自动驾驶感知\n"
         "- 智能家居终端"),
        
        ("知识产权",
         "已申请12项核心专利，其中3项已授权。\n"
         "形成了完整的专利布局，覆盖芯片架构、"
         "编译工具链、应用算法等核心技术领域。"),
        
        ("团队介绍",
         "研发团队来自清华大学微电子研究所，"
         "具有10年以上的AI芯片研发经验。\n"
         "团队成员曾在ISSCC、VLSI等顶级会议发表论文20余篇。"),
    ]
    
    for title, content in sections:
        # 标题
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50*mm, y_position, title)
        y_position -= 10*mm
        
        # 内容
        c.setFont("Helvetica", 11)
        # 处理多行文本
        lines = content.split('\n')
        for line in lines:
            c.drawString(50*mm, y_position, line)
            y_position -= 6*mm
        y_position -= 8*mm
    
    c.save()
    print(f"测试文档已生成: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_pdf()
