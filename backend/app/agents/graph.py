"""LangGraph agent workflow for sentiment analysis pipeline.

The graph defines three stages:
  1. Aggregate - Collect source data from various platforms
  2. Verify   - Filter, deduplicate, and validate relevance
  3. Score    - Run sentiment analysis on verified items

This is the initial skeleton. Each node will be expanded in Phase 2
with actual agent logic.
"""

from __future__ import annotations

import logging
import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    """State that flows through the sentiment analysis pipeline."""

    topic: str
    topic_id: str
    source_items: Annotated[list[dict[str, Any]], operator.add]
    verified_items: Annotated[list[dict[str, Any]], operator.add]
    scores: Annotated[list[dict[str, Any]], operator.add]
    status: str


async def aggregate(state: PipelineState) -> dict:
    """Collect data from configured sources for the given topic.

    In Phase 2, this node will fan out to multiple source-specific
    agents (Reddit, News API, Bluesky, etc.) and collect their results.
    """
    logger.info("Aggregating sources for topic: %s", state["topic"])
    # Placeholder: return empty list, real agents added in Phase 2
    return {"source_items": [], "status": "aggregated"}


async def verify(state: PipelineState) -> dict:
    """Filter, deduplicate, and validate relevance of source items.

    In Phase 2, this node will use an LLM to check relevance,
    remove duplicates, and filter low-quality content.
    """
    logger.info(
        "Verifying %d source items for topic: %s",
        len(state["source_items"]),
        state["topic"],
    )
    # Placeholder: pass all items through as verified
    return {"verified_items": state["source_items"], "status": "verified"}


async def score(state: PipelineState) -> dict:
    """Run sentiment analysis on verified items.

    In Phase 2, this node will use an LLM to produce structured
    sentiment scores for each verified item.
    """
    logger.info(
        "Scoring %d verified items for topic: %s",
        len(state["verified_items"]),
        state["topic"],
    )
    # Placeholder: return empty scores, real scoring added in Phase 2
    return {"scores": [], "status": "completed"}


def build_graph() -> StateGraph:
    """Build and compile the sentiment analysis pipeline graph."""
    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("aggregate", aggregate)
    graph.add_node("verify", verify)
    graph.add_node("score", score)

    # Define edges: linear pipeline for now
    graph.add_edge(START, "aggregate")
    graph.add_edge("aggregate", "verify")
    graph.add_edge("verify", "score")
    graph.add_edge("score", END)

    return graph.compile()


# Pre-built graph instance for use throughout the app
pipeline = build_graph()
