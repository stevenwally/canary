"""Sentiment scoring agent - produces structured sentiment analysis.

Uses an LLM to analyze the sentiment of verified source items,
producing nuanced scores with confidence levels, aspect breakdown,
and reasoning.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.schemas import SentimentResult, VerifiedItem
from app.core.llm import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a sentiment analysis agent. Your job is to analyze the sentiment of text \
content related to a specific topic.

For each item, produce a JSON object with:
- "overall_score": float from -1.0 (very negative) to 1.0 (very positive). \
0.0 is neutral.
- "confidence": float from 0.0 to 1.0 indicating how confident you are in the score
- "label": one of "positive", "negative", or "neutral"
  - positive: score > 0.15
  - negative: score < -0.15
  - neutral: score between -0.15 and 0.15
- "aspects": array of objects, each with:
  - "aspect": string - a specific sub-topic or entity mentioned
  - "score": float (-1.0 to 1.0)
  - "label": "positive", "negative", or "neutral"
  Only include aspects if the text discusses multiple distinct aspects. \
For short or simple texts, this can be an empty array.
- "reasoning": string - one or two sentences explaining the sentiment assessment

Important guidelines:
- Consider the overall tone, word choice, and context
- Sarcasm and irony should be detected when possible - flag lower confidence if unsure
- Distinguish between factual reporting (often neutral) and opinion/reaction
- Consider the source context (e.g. Reddit tends to be more informal/sarcastic)
- For news articles, focus on the framing and tone, not just the subject matter
- If content is mixed (both positive and negative), the overall score should reflect \
the balance, but flag key aspects separately

Return a JSON array of sentiment objects, one per input item, in the same order.\
"""

# Process items in batches to stay within context limits
BATCH_SIZE = 15


async def score_items(
    topic: str,
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Score sentiment for a batch of verified items.

    Args:
        topic: The keyword/topic being analyzed.
        items: List of VerifiedItem dicts from the verification stage.

    Returns:
        List of SentimentResult dicts, one per input item.
    """
    if not items:
        logger.info("No items to score")
        return []

    verified_items = [VerifiedItem(**item) for item in items]
    all_scores: list[dict[str, Any]] = []

    # Process in batches to avoid exceeding context window
    for batch_start in range(0, len(verified_items), BATCH_SIZE):
        batch = verified_items[batch_start : batch_start + BATCH_SIZE]
        batch_scores = await _score_batch(topic, batch)
        all_scores.extend(batch_scores)

    logger.info(
        "Scored %d items for topic '%s'",
        len(all_scores),
        topic,
    )
    return all_scores


async def _score_batch(
    topic: str,
    items: list[VerifiedItem],
) -> list[dict[str, Any]]:
    """Score a single batch of items."""
    items_text = _format_items_for_prompt(items)

    llm = get_llm()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Topic: {topic}\n\n"
                    f"Analyze the sentiment of these {len(items)} items:\n\n"
                    f"{items_text}"
                )
            ),
        ],
        response_format={"type": "json_object"},
    )

    try:
        result = json.loads(response.content)
        logger.info("Sentiment LLM response type: %s", type(result).__name__)

        if isinstance(result, list):
            scores = result
        elif isinstance(result, dict):
            # Try common keys the LLM might use
            for key in ("items", "scores", "results", "sentiments", "data", "analyses"):
                if key in result and isinstance(result[key], list):
                    scores = result[key]
                    logger.info("Found scores under key '%s'", key)
                    break
            else:
                # Fallback: use the first list value found
                list_values = [v for v in result.values() if isinstance(v, list)]
                if list_values:
                    scores = list_values[0]
                    logger.info("Found scores in first list value (%d items)", len(scores))
                else:
                    logger.error(
                        "Unexpected sentiment response structure: %s",
                        list(result.keys()),
                    )
                    scores = []
        else:
            scores = []

        logger.info("Parsed %d scores from LLM response", len(scores))
    except (json.JSONDecodeError, AttributeError):
        logger.error("Failed to parse sentiment LLM response: %s", response.content)
        # Fallback: return neutral scores
        return [
            SentimentResult(
                overall_score=0.0,
                confidence=0.0,
                label="neutral",
                aspects=None,
                reasoning="Sentiment analysis failed, defaulting to neutral",
            ).model_dump()
            for _ in items
        ]

    # Validate and normalize each score
    validated: list[dict[str, Any]] = []
    for i, raw_score in enumerate(scores):
        try:
            sentiment = SentimentResult(
                overall_score=_clamp(raw_score.get("overall_score", 0.0), -1.0, 1.0),
                confidence=_clamp(raw_score.get("confidence", 0.5), 0.0, 1.0),
                label=_normalize_label(raw_score.get("label", "neutral")),
                aspects=raw_score.get("aspects"),
                reasoning=raw_score.get("reasoning", "No reasoning provided"),
            )
            validated.append(sentiment.model_dump())
        except Exception:
            logger.exception("Failed to validate score for item %d", i)
            validated.append(
                SentimentResult(
                    overall_score=0.0,
                    confidence=0.0,
                    label="neutral",
                    aspects=None,
                    reasoning="Score validation failed",
                ).model_dump()
            )

    return validated


def _format_items_for_prompt(items: list[VerifiedItem]) -> str:
    """Format verified items for the scoring prompt."""
    parts = []
    for i, item in enumerate(items):
        text_preview = item.text[:800] + "..." if len(item.text) > 800 else item.text
        parts.append(
            f"[Item {i}]\n"
            f"Source: {item.source}\n"
            f"Title: {item.title or '(none)'}\n"
            f"Text: {text_preview}\n"
        )
    return "\n".join(parts)


def _clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value to a range."""
    return max(min_val, min(max_val, float(value)))


def _normalize_label(label: str) -> str:
    """Normalize a sentiment label to one of the three valid values."""
    label = label.lower().strip()
    if label in ("positive", "negative", "neutral"):
        return label
    if "pos" in label:
        return "positive"
    if "neg" in label:
        return "negative"
    return "neutral"
