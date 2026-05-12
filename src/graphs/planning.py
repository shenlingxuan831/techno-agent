"""工作流规划：按用户类型、显式配置与模型输出裁剪并行分支。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Set

from graphs.state import ALL_PARALLEL_TRACKS

USER_TYPE_DEFAULT_TRACKS: Dict[str, List[str]] = {
    "高校": list(ALL_PARALLEL_TRACKS),
    "企业": list(ALL_PARALLEL_TRACKS),
    # 政府侧重政策与需求对接，弱关联直接募资匹配
    "政府": ["match_requirements", "policy_search", "bp_generation"],
    # 投资机构侧重需求与资本路径及 BP
    "投资机构": ["match_requirements", "capital_match", "bp_generation"],
}

_ALLOWED: Set[str] = set(ALL_PARALLEL_TRACKS)


def normalize_requested_tracks(requested: Optional[Sequence[str]]) -> Optional[List[str]]:
    """过滤非法 id；若为空列表则视为未指定。"""
    if not requested:
        return None
    out = [t for t in requested if t in _ALLOWED]
    return out or None


def _pick_focus_intersection(base: List[str], focus: Sequence[str]) -> List[str]:
    """若模型给出了 downstream_focus（元素为合法节点 id），与 base 求交。"""
    focus_ids = [t for t in focus if t in _ALLOWED]
    if not focus_ids:
        return base
    inter = [t for t in base if t in set(focus_ids)]
    return inter or base


def build_enabled_tracks(
    *,
    user_type: str,
    workflow_tracks: Optional[Sequence[str]],
    downstream_focus: Sequence[str],
    commercial_next_steps: Sequence[str],
) -> tuple[List[str], Dict[str, Any]]:
    """
    返回 (enabled_tracks, reasons)。
    commercial_next_steps 中若包含合法节点 id，也会参与求交（可选信号）。
    """
    reasons: Dict[str, Any] = {"user_type": user_type}

    explicit = normalize_requested_tracks(list(workflow_tracks) if workflow_tracks else None)
    if explicit is not None:
        reasons["source"] = "explicit_workflow_tracks"
        reasons["tracks"] = explicit
        return sorted(explicit), reasons

    base = list(USER_TYPE_DEFAULT_TRACKS.get(user_type, list(ALL_PARALLEL_TRACKS)))
    reasons["source"] = "user_type_default"
    reasons["tracks_before_focus"] = list(base)

    merged = _pick_focus_intersection(base, list(downstream_focus))
    if merged != base:
        reasons["downstream_focus_applied"] = list(downstream_focus)
        reasons["intersection"] = "downstream_focus"
    base = merged

    step_ids = [t for t in commercial_next_steps if t in _ALLOWED]
    if step_ids:
        narrowed = [t for t in base if t in set(step_ids)]
        if len(narrowed) < len(base):
            reasons["commercial_next_steps_applied"] = list(step_ids)
            base = narrowed or base

    reasons["tracks_final"] = list(base)
    return sorted(base), reasons


def should_skip_track(enabled_tracks: Optional[Sequence[str]], track_id: str) -> bool:
    """enabled_tracks 非空且不含本节点 id 时跳过 LLM。"""
    if enabled_tracks is None:
        return False
    return track_id not in set(enabled_tracks)
