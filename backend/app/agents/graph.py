"""LangGraph agent workflow for sentiment analysis pipeline.

The graph defines three stages:
  1. Aggregate - Fan out to multiple source agents concurrently
  2. Verify   - LLM-powered relevance filtering and deduplication
  3. Score    - LLM-powered sentiment analysis on verified items
"""

from __future__ import annotations

import asyncio
import logging
import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.sentiment import score_items
from app.agents.sources import BlueskyAgent, NewsAPIAgent, RedditAgent
from app.agents.verification import verify_items

logger = logging.getLogger(__name__)

# All available source agents
SOURCE_AGENTS = [
    RedditAgent(),
    NewsAPIAgent(),
    BlueskyAgent(),
]


class PipelineState(TypedDict):
    """State that flows through the sentiment analysis pipeline."""

    topic: str
    topic_id: str
    source_items: Annotated[list[dict[str, Any]], operator.add]
    verified_items: Annotated[list[dict[str, Any]], operator.add]
    scores: Annotated[list[dict[str, Any]], operator.add]
    status: str


async def aggregate(state: PipelineState) -> dict:
    """Collect data from all configured sources concurrently.

    Fans out to Reddit, NewsAPI, and Bluesky agents in parallel.
    Each agent that fails gracefully returns an empty list.
    """
    topic = state["topic"]
    logger.info("Aggregating sources for topic: '%s'", topic)

    # Run all source agents concurrently
    tasks = [agent.safe_fetch(topic, max_items=30) for agent in SOURCE_AGENTS]
    results = await asyncio.gather(*tasks)

    # Flatten all results into a single list of dicts
    all_items: list[dict[str, Any]] = []
    for agent, items in zip(SOURCE_AGENTS, results):
        logger.info("  %s: %d items", agent.name, len(items))
        all_items.extend(item.model_dump() for item in items)

    logger.info("Total aggregated: %d items", len(all_items))
    return {"source_items": all_items, "status": "aggregated"}


async def verify(state: PipelineState) -> dict:
    """Filter, deduplicate, and validate relevance of source items."""
    topic = state["topic"]
    items = state["source_items"]

    logger.info("Verifying %d source items for topic: '%s'", len(items), topic)

    if not items:
        return {"verified_items": [], "status": "verified"}

    verified = await verify_items(topic, items)

    logger.info("Verification passed: %d/%d items", len(verified), len(items))
    return {"verified_items": verified, "status": "verified"}


async def score(state: PipelineState) -> dict:
    """Run sentiment analysis on verified items."""
    topic = state["topic"]
    verified = state["verified_items"]

    logger.info("Scoring %d verified items for topic: '%s'", len(verified), topic)

    if not verified:
        return {"scores": [], "status": "completed"}

    scores = await score_items(topic, verified)

    logger.info("Scored %d items", len(scores))
    return {"scores": scores, "status": "completed"}


def build_graph() -> StateGraph:
    """Build and compile the sentiment analysis pipeline graph."""
    graph = StateGraph(PipelineState)

    graph.add_node("aggregate", aggregate)
    graph.add_node("verify", verify)
    graph.add_node("score", score)

    graph.add_edge(START, "aggregate")
    graph.add_edge("aggregate", "verify")
    graph.add_edge("verify", "score")
    graph.add_edge("score", END)

    return graph.compile()


# Pre-built graph instance
pipeline = build_graph()
