"""与 workspace 路径、源文件读取相关的底层 I/O（nodes 与 services 共用，避免循环导入）。"""

from __future__ import annotations

import os
from pathlib import Path


def workspace_root() -> Path:
    return Path(os.getenv("COZE_WORKSPACE_PATH", os.getcwd())).resolve()


def read_source_text(source_uri: str, max_chars: int = 50_000) -> str:
    """Best-effort read local file; otherwise return placeholder."""
    if not source_uri.strip():
        return "[stub] 未提供 source_uri。"
    p = Path(source_uri)
    if not p.is_absolute():
        p = workspace_root() / p
    if p.is_file():
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
            if len(raw) > max_chars:
                return raw[:max_chars] + "\n\n…（已截断）"
            return raw
        except OSError:
            return f"[stub] 无法读取文件: {p}"
    return f"[stub] 路径不存在或非文件: {p} — 请在 payload 中填写正确 source_uri。"
