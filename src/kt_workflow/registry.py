"""DAG 注册表：与 graph.py 中节点 id 一致（便于对照文档与排查）。"""

# 顺序 = 实际执行顺序（ingest → … → pdf）；正文章为 0..10 共 11 个 chapter 节点
PIPELINE_NODE_IDS: tuple[str, ...] = (
    "kt_ingest",
    "kt_extract",
    "kt_structure",
    "kt_chapter_00",
    "kt_chapter_01",
    "kt_chapter_02",
    "kt_chapter_03",
    "kt_chapter_04",
    "kt_chapter_05",
    "kt_chapter_06",
    "kt_chapter_07",
    "kt_chapter_08",
    "kt_chapter_09",
    "kt_chapter_10",
    "kt_aggregate",
    "kt_polish",
    "kt_pdf",
)
