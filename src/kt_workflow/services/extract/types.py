"""Extract pipeline result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FigureRecord:
    fig_id: str
    page: int | None
    storage_uri: str
    caption: str = ""
    figure_type: str = "unknown"
    width: int | None = None
    height: int | None = None
    priority_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "fig_id": self.fig_id,
            "page": self.page,
            "storage_uri": self.storage_uri,
            "caption": self.caption,
            "figure_type": self.figure_type,
            "width": self.width,
            "height": self.height,
            "priority_score": self.priority_score,
        }


@dataclass
class ExtractResult:
    plain_text: str
    markdown: str
    figures: list[FigureRecord] = field(default_factory=list)
    figure_analysis: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def analyze_text(self) -> str:
        """供 kt_analyze 优先使用的正文（Markdown 优先）。"""
        md = (self.markdown or "").strip()
        if md and not md.startswith("[extract]"):
            return md
        return (self.plain_text or "").strip()
