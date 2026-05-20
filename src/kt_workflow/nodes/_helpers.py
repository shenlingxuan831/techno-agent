"""Shared helpers for nodes (keep node files thin)."""

from __future__ import annotations

import json
from typing import Any

from kt_workflow.text_io import read_source_text, workspace_root


def safe_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


__all__ = ["read_source_text", "workspace_root", "safe_json_dumps"]
