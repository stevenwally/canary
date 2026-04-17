"""Verification agent - filters and validates aggregated source items.

Uses an LLM to assess relevance, detect duplicates, and filter
low-quality content before it reaches the sentiment scoring stage.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.schemas import RawSourceItem, VerifiedItem
from app.core.llm import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a content verification agent for a sentiment analysis system.

Your job is to evaluate whether a piece of text content is relevant to a given \
topic/keyword and is of sufficient quality for sentiment analysis.

For each item, you must output a JSON object with:
- "relevant": boolean - whether the content is meaningfully about the topic
- "relevance_score": float (0.0 to 1.0) - how relevant (0 = not at all, 1 = highly)
- "reason": string - one sentence explaining your decision
- "is_duplicate_of": integer or null - if this item is a near-duplicate of a \
previous item in the batch, provide that item's index (0-based). Otherwise null.

Rules:
- Content that only tangentially mentions the topic should score below 0.3
- Content that is primarily about the topic should score above 0.7
- Very short content (under 20 characters of substance) is low quality -> not relevant
- Spam, ads, or purely promotional content -> not relevant
- If content is in a language other than English, still evaluate it if you can, \
otherwise mark it as not relevant

Return a JSON array of objects, one per input item, in the same order.\
"""


async def verify_items(
    topic: str,
    items: list[dict[str, Any]],
    relevance_threshold: float = 0.4,
) -> list[dict[str, Any]]:
    """Verify a batch of source items for relevance and quality.

    Args:
        topic: The keyword/topic being analyzed.
        items: List of RawSourceItem dicts from the aggregation stage.
        relevance_threshold: Minimum relevance score to keep an item.

    Returns:
        List of VerifiedItem dicts (items that passed verification).
    """
    if not items:
        logger.info("No items to verify")
        return []

    # Parse into RawSourceItem objects for type safety
    raw_items = [RawSourceItem(**item) for item in items]

    # Build the prompt with all items
    items_text = _format_items_for_prompt(raw_items)

    llm = get_llm()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"Topic: {topic}\n\nEvaluate these {len(raw_items)} items:\n\n{items_text}"
            ),
        ],
        response_format={"type": "json_object"},
    )

    # Parse LLM response
    import json

    try:
        result = json.loads(response.content)
        logger.info("Verification LLM response type: %s", type(result).__name__)

        # Handle various response formats from the LLM
        if isinstance(result, list):
            evaluations = result
        elif isinstance(result, dict):
            # Try common keys the LLM might use
            for key in ("items", "evaluations", "results", "data"):
                if key in result and isinstance(result[key], list):
                    evaluations = result[key]
                    break
            else:
                # If it's a single-item dict with a list value, use that
                list_values = [v for v in result.values() if isinstance(v, list)]
                if list_values:
                    evaluations = list_values[0]
                else:
                    logger.error(
                        "Unexpected verification response structure: %s",
                        list(result.keys()),
                    )
                    evaluations = []
        else:
            evaluations = []

        logger.info("Parsed %d evaluations from LLM response", len(evaluations))
    except (json.JSONDecodeError, AttributeError):
        logger.error("Failed to parse verification LLM response: %s", response.content)
        # Fallback: pass everything through
        return [
            VerifiedItem(
                **item.model_dump(),
                relevance_score=0.5,
                relevance_reason="Verification failed, passed through by default",
            ).model_dump()
            for item in raw_items
        ]

    # Filter and transform
    verified: list[dict[str, Any]] = []
    seen_duplicate_targets: set[int] = set()

    for i, (raw_item, evaluation) in enumerate(zip(raw_items, evaluations)):
        is_relevant = evaluation.get("relevant", True)
        score = evaluation.get("relevance_score", 0.5)
        reason = evaluation.get("reason", "No reason provided")
        duplicate_of = evaluation.get("is_duplicate_of")

        # Skip if explicitly not relevant or below threshold
        if not is_relevant or score < relevance_threshold:
            logger.info("Filtered item %d: relevant=%s score=%.2f reason='%s'", i, is_relevant, score, reason)
            continue

        # Skip duplicates
        if duplicate_of is not None and isinstance(duplicate_of, int):
            logger.info("Filtered item %d: duplicate of item %d", i, duplicate_of)
            seen_duplicate_targets.add(duplicate_of)
            continue

        verified_item = VerifiedItem(
            **raw_item.model_dump(),
            relevance_score=score,
            relevance_reason=reason,
        )
        verified.append(verified_item.model_dump())

    logger.info(
        "Verification: %d/%d items passed (topic='%s')",
        len(verified),
        len(raw_items),
        topic,
    )
    return verified


def _format_items_for_prompt(items: list[RawSourceItem]) -> str:
    """Format items into a numbered list for the LLM prompt."""
    parts = []
    for i, item in enumerate(items):
        text_preview = item.text[:500] + "..." if len(item.text) > 500 else item.text
        parts.append(
            f"[Item {i}]\n"
            f"Source: {item.source}\n"
            f"Title: {item.title or '(none)'}\n"
            f"Text: {text_preview}\n"
        )
    return "\n".join(parts)
