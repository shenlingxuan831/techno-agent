"""DeepSeek / OpenAI 兼容网关，供 kt_workflow 各 service 调用。"""

from __future__ import annotations

import os

from coze_coding_dev_sdk import LLMClient
from coze_coding_dev_sdk.core.config import Config


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def analysis_mock_enabled() -> bool:
    return _env_truthy("KT_ANALYSIS_MOCK_LLM")


def kt_llm_client() -> LLMClient:
    """优先 DeepSeek；可回退 OPENAI_* / ARK_*。"""
    key = (
        (os.getenv("DEEPSEEK_API_KEY") or "").strip()
        or (os.getenv("OPENAI_API_KEY") or "").strip()
        or (os.getenv("ARK_API_KEY") or "").strip()
        or (os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY") or "").strip()
    )
    base_url = (
        (os.getenv("DEEPSEEK_BASE_URL") or "").strip()
        or (os.getenv("OPENAI_BASE_URL") or "").strip()
        or (os.getenv("COZE_INTEGRATION_BASE_URL") or "").strip()
        or "https://api.deepseek.com"
    )
    if key:
        return LLMClient(
            config=Config(api_key=key, base_url=base_url, base_model_url=base_url)
        )
    return LLMClient()


def kt_llm_model(default: str = "deepseek-chat") -> str:
    return (
        (os.getenv("DEEPSEEK_MODEL") or "").strip()
        or (os.getenv("ARK_MODEL") or "").strip()
        or (os.getenv("ARK_ENDPOINT_ID") or "").strip()
        or default
    )
