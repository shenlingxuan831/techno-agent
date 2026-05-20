from pathlib import Path
import re

meta = {
    0: ("文档说明", "Chapter00Writer", "chapter_00.py"),
    1: ("执行摘要", "Chapter01Writer", "chapter_01.py"),
    2: ("项目背景与概述", "Chapter02Writer", "chapter_02.py"),
    3: ("核心技术与科研成果", "Chapter03Writer", "chapter_03.py"),
    4: ("市场分析", "Chapter04Writer", "chapter_04.py"),
    5: ("商业化落地方案", "Chapter05Writer", "chapter_05.py"),
    6: ("运营团队与组织规划", "Chapter06Writer", "chapter_06.py"),
    7: ("财务规划", "Chapter07Writer", "chapter_07.py"),
    8: ("风险分析与应对", "Chapter08Writer", "chapter_08.py"),
    9: ("结论与展望", "Chapter09Writer", "chapter_09.py"),
    10: ("附录 A～F", "Chapter10Writer", "chapter_10.py"),
}
base = Path(__file__).resolve().parents[1] / "src" / "kt_workflow" / "nodes" / "chapters"
for n, (title, writer, fn) in meta.items():
    p = base / f"node_chapter_{n:02d}.py"
    text = p.read_text(encoding="utf-8")
    new_doc = (
        f'"""章 {n}：{title}。\n\n'
        f"图节点 kt_chapter_{n:02d} → chapter_runner(chapter={n}) → {writer}\n"
        f"组员实现文件：kt_workflow/services/chapter_writers/{fn}（本节点一般无需修改）\n"
        f'"""'
    )
    text = re.sub(r'"""[\s\S]*?"""', new_doc, text, count=1)
    p.write_text(text, encoding="utf-8")
    print("patched", p.name)
