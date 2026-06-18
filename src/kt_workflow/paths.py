"""Repository-root paths for kt_workflow local storage (var/kt_workflow/...)."""

from __future__ import annotations

from pathlib import Path


def kt_repo_root() -> Path:
    """slx_01 仓库根（本文件位于 src/kt_workflow/paths.py）。"""
    return Path(__file__).resolve().parents[2]


def kt_var_root() -> Path:
    base = kt_repo_root() / "var" / "kt_workflow"
    base.mkdir(parents=True, exist_ok=True)
    return base


def kt_databases_dir() -> Path:
    d = kt_var_root() / "databases"
    d.mkdir(parents=True, exist_ok=True)
    return d


def kt_runs_root() -> Path:
    d = kt_var_root() / "runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def kt_run_output_dir(run_id: str) -> Path:
    d = kt_runs_root() / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def kt_run_source_dir(run_id: str) -> Path:
    """单次 run 的源文件解析产物：MinerU Markdown、抽取图片等。"""
    d = kt_run_output_dir(run_id) / "source"
    d.mkdir(parents=True, exist_ok=True)
    return d


def kt_cache_root() -> Path:
    """大体积缓存（MinerU / HuggingFace / pip）统一放仓库 var/cache，避免占 C 盘。"""
    d = kt_repo_root() / "var" / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d

