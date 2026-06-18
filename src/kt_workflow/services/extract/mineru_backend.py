"""Layer 1 — MinerU PDF 解析（GPU pipeline，中英文论文）。"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from kt_workflow.services.extract.cache_env import apply_extract_cache_env

def mineru_available() -> bool:
    if _mineru_cli_path().is_file():
        return True
    if shutil.which("mineru"):
        return True
    if _mineru_python_path().is_file():
        return True
    try:
        import mineru  # noqa: F401

        return True
    except ImportError:
        return False


def _mineru_python_path() -> Path:
    raw = (os.getenv("KT_MINERU_PYTHON") or "").strip()
    if raw:
        return Path(raw)
    # Default: sibling venv .venv-extract (Python 3.12) on repo root
    from kt_workflow.paths import kt_repo_root

    return kt_repo_root() / ".venv-extract" / "Scripts" / "python.exe"


def _mineru_cli_path() -> Path:
    raw = (os.getenv("KT_MINERU_CLI") or "").strip()
    if raw:
        return Path(raw)
    from kt_workflow.paths import kt_repo_root

    return kt_repo_root() / ".venv-extract" / "Scripts" / "mineru.exe"


def _mineru_lang() -> str:
    return os.getenv("KT_MINERU_LANG", "ch").strip() or "ch"


def _mineru_backend() -> str:
    return os.getenv("KT_MINERU_BACKEND", "pipeline").strip() or "pipeline"


def _find_markdown(output_dir: Path) -> Path | None:
    candidates = sorted(output_dir.rglob("*.md"), key=lambda p: len(p.parts))
    for path in candidates:
        if path.name.startswith("."):
            continue
        if path.stat().st_size > 0:
            return path
    return None


def _run_mineru_cli(pdf_path: Path, output_dir: Path) -> None:
    apply_extract_cache_env()
    output_dir.mkdir(parents=True, exist_ok=True)
    cli = _mineru_cli_path()
    py = _mineru_python_path()
    if cli.is_file():
        cmd = [str(cli)]
    elif py.is_file():
        cmd = [str(py), "-m", "mineru"]
    elif shutil.which("mineru"):
        cmd = ["mineru"]
    else:
        raise FileNotFoundError(
            "未找到 MinerU。请运行 scripts/install_extract_deps.ps1 并配置 KT_MINERU_CLI"
        )
    cmd.extend(
        [
            "-p",
            str(pdf_path),
            "-o",
            str(output_dir),
            "-b",
            _mineru_backend(),
            "-l",
            _mineru_lang(),
        ]
    )
    if os.getenv("KT_MINERU_METHOD", "").strip():
        cmd.extend(["-m", os.getenv("KT_MINERU_METHOD", "").strip()])
    env = os.environ.copy()
    subprocess.run(cmd, check=True, timeout=int(os.getenv("KT_MINERU_TIMEOUT", "900")), env=env)


def _run_mineru_python(pdf_path: Path, output_dir: Path) -> None:
    apply_extract_cache_env()
    py = _mineru_python_path()
    if py.is_file():
        import subprocess as sp

        output_dir.mkdir(parents=True, exist_ok=True)
        # Delegate to CLI module in extract venv when import in main venv fails
        script = (
            "from mineru.cli.common import do_parse; "
            "import pathlib; p=pathlib.Path(r'%s'); "
            "do_parse(output_dir=r'%s', pdf_file_names=[p.name], "
            "pdf_bytes_list=[p.read_bytes()], p_lang_list=['%s'], "
            "backend='%s', parse_method='%s', formula_enable=True, table_enable=True)"
            % (
                str(pdf_path).replace("\\", "\\\\"),
                str(output_dir).replace("\\", "\\\\"),
                _mineru_lang(),
                _mineru_backend(),
                os.getenv("KT_MINERU_METHOD", "auto"),
            )
        )
        sp.run([str(py), "-c", script], check=True, env=os.environ.copy())
        return

    from mineru.cli.common import do_parse

    output_dir.mkdir(parents=True, exist_ok=True)
    data = pdf_path.read_bytes()
    do_parse(
        output_dir=str(output_dir),
        pdf_file_names=[pdf_path.name],
        pdf_bytes_list=[data],
        p_lang_list=[_mineru_lang()],
        backend=_mineru_backend(),
        parse_method=os.getenv("KT_MINERU_METHOD", "auto"),
        formula_enable=True,
        table_enable=True,
    )


def parse_pdf_with_mineru(
    pdf_path: Path,
    output_dir: Path,
) -> tuple[str, Path | None, dict[str, Any]]:
    """
    返回 (markdown_text, markdown_path, meta)。
    markdown_path 用于定位 images/ 子目录。
    """
    meta: dict[str, Any] = {
        "backend": "mineru",
        "mineru_backend": _mineru_backend(),
        "mineru_lang": _mineru_lang(),
    }
    work_dir = output_dir / "mineru_raw"
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        if _mineru_cli_path().is_file() or _mineru_python_path().is_file() or shutil.which("mineru"):
            _run_mineru_cli(pdf_path, work_dir)
            meta["invocation"] = "cli"
        else:
            _run_mineru_python(pdf_path, work_dir)
            meta["invocation"] = "python"
    except subprocess.CalledProcessError as exc:
        meta["error"] = f"mineru_cli_failed:{exc.returncode}"
        raise
    except Exception as exc:
        meta["error"] = f"mineru_failed:{exc}"
        raise

    md_path = _find_markdown(work_dir)
    if md_path is None:
        meta["error"] = "mineru_no_markdown"
        return "", None, meta

    markdown = md_path.read_text(encoding="utf-8", errors="replace")
    meta["markdown_path"] = str(md_path)
    meta["mineru_work_dir"] = str(work_dir)
    return markdown, md_path, meta
