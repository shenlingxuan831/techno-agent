"""将 MinerU / HuggingFace / pip 缓存重定向到项目 var/cache（通常在 E 盘仓库内）。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from kt_workflow.paths import kt_cache_root, kt_repo_root


def _truthy(name: str, default: str = "1") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes")


def apply_extract_cache_env(*, force: bool = False) -> dict[str, str]:
    """
    设置进程级环境变量，使模型与 pip 缓存落在 <repo>/var/cache/。
    已显式设置的环境变量不会被覆盖（除非 force=True）。
    """
    if not _truthy("KT_CACHE_ON_PROJECT", "1"):
        return {}

    cache = kt_cache_root()
    dirs = {
        "pip": cache / "pip",
        "huggingface": cache / "huggingface",
        "hf_hub": cache / "huggingface" / "hub",
        "modelscope": cache / "modelscope",
        "mineru": cache / "mineru",
        "mineru_models": cache / "mineru" / "models",
        "tmp": cache / "tmp",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    mineru_json = dirs["mineru"] / "mineru.json"
    _ensure_mineru_json(mineru_json, dirs["mineru_models"])

    mapping = {
        "PIP_CACHE_DIR": str(dirs["pip"]),
        "HF_HOME": str(dirs["huggingface"]),
        "HUGGINGFACE_HUB_CACHE": str(dirs["hf_hub"]),
        "MODELSCOPE_CACHE": str(dirs["modelscope"]),
        "MINERU_TOOLS_CONFIG_JSON": str(mineru_json),
        "TMP": str(dirs["tmp"]),
        "TEMP": str(dirs["tmp"]),
    }
    if not os.getenv("MINERU_MODEL_SOURCE"):
        mapping["MINERU_MODEL_SOURCE"] = os.getenv("KT_MINERU_MODEL_SOURCE", "modelscope")

    applied: dict[str, str] = {}
    for key, value in mapping.items():
        if force or not os.getenv(key):
            os.environ[key] = value
            applied[key] = value
    return applied


def _ensure_mineru_json(config_path: Path, models_dir: Path) -> None:
    """预写 mineru.json，使 pipeline 模型目录指向项目 var/cache。"""
    pipeline_dir = models_dir / "pipeline"
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "models-dir": {
            "pipeline": str(pipeline_dir),
            "vlm": str(models_dir / "vlm"),
        }
    }
    if config_path.is_file():
        try:
            existing = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(existing, dict) and existing.get("models-dir"):
                return
        except (json.JSONDecodeError, OSError):
            pass
    config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def cache_locations_summary() -> dict[str, str]:
    """返回当前缓存路径说明（供日志/文档）。"""
    cache = kt_cache_root()
    return {
        "repo_root": str(kt_repo_root()),
        "cache_root": str(cache),
        "venv": str(kt_repo_root() / ".venv"),
        "note": "Python 包装 .venv；MinerU/HF 模型在 var/cache（均在仓库盘符，默认 E:）",
    }
