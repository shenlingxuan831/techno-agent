"""Local-only: replace Coze Loop remote client with an in-process no-op (no trace ingest)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from cozeloop import set_default_client
from cozeloop.client import Client
from cozeloop.entities.prompt import Prompt, Message, PromptVariable, ExecuteResult
from cozeloop.entities.stream import StreamReader
from cozeloop.span import SpanContext, Span
from cozeloop._noop import NOOP_SPAN


class _SilentLocalLoopClient(Client):
    """Satisfies cozeloop.Client; tracing and prompt hub calls are no-ops / not implemented."""

    @property
    def workspace_id(self) -> str:
        return "local"

    def close(self) -> None:
        return

    def get_prompt(self, prompt_key: str, version: str = "", label: str = "") -> Optional[Prompt]:
        return None

    def prompt_format(
        self, prompt: Prompt, variables: Dict[str, PromptVariable]
    ) -> List[Message]:
        raise NotImplementedError("Coze Loop prompt hub disabled in local mode")

    def execute_prompt(
        self,
        prompt_key: str,
        *,
        version: Optional[str] = None,
        label: Optional[str] = None,
        variable_vals: Optional[Dict[str, Any]] = None,
        messages: Optional[List[Message]] = None,
        stream: bool = False,
        timeout: Optional[int] = None,
    ) -> Union[ExecuteResult, StreamReader[ExecuteResult]]:
        raise NotImplementedError("Coze Loop prompt hub disabled in local mode")

    async def aexecute_prompt(
        self,
        prompt_key: str,
        *,
        version: Optional[str] = None,
        label: Optional[str] = None,
        variable_vals: Optional[Dict[str, Any]] = None,
        messages: Optional[List[Message]] = None,
        stream: bool = False,
        timeout: Optional[int] = None,
    ) -> Union[ExecuteResult, StreamReader[ExecuteResult]]:
        raise NotImplementedError("Coze Loop prompt hub disabled in local mode")

    def start_span(
        self,
        name: str,
        span_type: str,
        *,
        start_time: Optional[int] = None,
        child_of: Optional[SpanContext] = None,
        start_new_trace: bool = False,
    ) -> Span:
        return NOOP_SPAN

    def get_span_from_context(self) -> Span:
        return NOOP_SPAN

    def get_span_from_header(self, header: Dict[str, str]) -> SpanContext:
        return NOOP_SPAN

    def flush(self) -> None:
        return


def install_silent_loop_client() -> None:
    set_default_client(_SilentLocalLoopClient())
