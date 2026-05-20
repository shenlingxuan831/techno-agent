"""加载《科研成果商业化项目商业计划书》模块注册表（config/bp_transform_outline_registry.json）。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, List, TypedDict


class BpModuleSpec(TypedDict, total=False):
    id: str
    chapter: int
    ref: str
    title: str
    needs_chart: bool
    writer_hint: str


class BpRegistry(TypedDict, total=False):
    document_title: str
    registry_version: int
    artifact_conventions: dict[str, str]
    outline_spec_md: str
    outline_templates_md: str
    modules: List[BpModuleSpec]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def registry_path() -> Path:
    return _repo_root() / "config" / "bp_transform_outline_registry.json"


@lru_cache(maxsize=1)
def load_registry() -> BpRegistry:
    path = registry_path()
    if not path.is_file():
        raise FileNotFoundError(f"缺少注册表: {path}（可运行 scripts/build_bp_transform_registry.py 生成）")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data  # type: ignore[return-value]


def modules_for_chapter(chapter: int) -> list[BpModuleSpec]:
    return [m for m in load_registry()["modules"] if int(m["chapter"]) == chapter]


def all_modules_in_order() -> list[BpModuleSpec]:
    return list(load_registry()["modules"])
