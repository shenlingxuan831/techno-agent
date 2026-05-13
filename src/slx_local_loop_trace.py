"""LangGraph run config without importing coze_coding_utils.log.loop_trace (avoids remote Loop client)."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from coze_coding_utils.log.node_log import Logger


def init_run_config(graph, ctx):
    tracer = Logger(graph, ctx)
    tracer.on_chain_start = tracer.on_chain_start_graph
    tracer.on_chain_end = tracer.on_chain_end_graph
    return RunnableConfig(callbacks=[tracer])


def init_agent_config(graph, ctx):
    return RunnableConfig(callbacks=[])
