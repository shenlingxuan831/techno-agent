"""按 chapter 数字（0～10）注册 Writer 实例，供 chapter_runner 调用。"""

from __future__ import annotations

from kt_workflow.services.chapter_writer_contract import ChapterModuleWriter
from kt_workflow.services.chapter_writers.chapter_00 import Chapter00Writer
from kt_workflow.services.chapter_writers.chapter_01 import Chapter01Writer
from kt_workflow.services.chapter_writers.chapter_02 import Chapter02Writer
from kt_workflow.services.chapter_writers.chapter_03 import Chapter03Writer
from kt_workflow.services.chapter_writers.chapter_04 import Chapter04Writer
from kt_workflow.services.chapter_writers.chapter_05 import Chapter05Writer
from kt_workflow.services.chapter_writers.chapter_06 import Chapter06Writer
from kt_workflow.services.chapter_writers.chapter_07 import Chapter07Writer
from kt_workflow.services.chapter_writers.chapter_08 import Chapter08Writer
from kt_workflow.services.chapter_writers.chapter_09 import Chapter09Writer
from kt_workflow.services.chapter_writers.chapter_10 import Chapter10Writer

_WRITERS: dict[int, ChapterModuleWriter] = {
    0: Chapter00Writer(),
    1: Chapter01Writer(),
    2: Chapter02Writer(),
    3: Chapter03Writer(),
    4: Chapter04Writer(),
    5: Chapter05Writer(),
    6: Chapter06Writer(),
    7: Chapter07Writer(),
    8: Chapter08Writer(),
    9: Chapter09Writer(),
    10: Chapter10Writer(),
}


def get_chapter_writer(chapter: int) -> ChapterModuleWriter:
    if chapter not in _WRITERS:
        raise ValueError(f"未注册的 chapter={chapter}，请在 services/chapter_writers/__init__.py 登记")
    return _WRITERS[chapter]
