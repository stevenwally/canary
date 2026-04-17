"""Shared Pydantic schemas for agent input/output.

These schemas define the common data contract between agents.
Every source agent produces RawSourceItems, the verification agent
produces VerifiedItems, and the scoring agent produces ScoredItems.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RawSourceItem(BaseModel):
    """A single piece of content collected from a source.

    This is the output format for all aggregation agents.
    """

    source: str = Field(description="Source platform (e.g. 'reddit', 'newsapi', 'bluesky')")
    external_id: str | None = Field(default=None, description="Source-specific unique ID")
    title: str | None = Field(default=None, description="Title/headline if available")
    text: str = Field(description="Main text content")
    author: str | None = Field(default=None, description="Author/username")
    url: str | None = Field(default=None, description="URL to original content")
    published_at: datetime | None = Field(default=None, description="Publication timestamp")
    metadata: dict | None = Field(default=None, description="Source-specific extra data")


class VerifiedItem(RawSourceItem):
    """A source item that has passed verification.

    Extends RawSourceItem with verification metadata.
    """

    relevance_score: float = Field(
        description="How relevant this item is to the topic (0.0-1.0)"
    )
    relevance_reason: str = Field(
        description="Brief explanation of relevance assessment"
    )


class SentimentResult(BaseModel):
    """Sentiment analysis result for a single item."""

    overall_score: float = Field(
        description="Sentiment score from -1.0 (very negative) to 1.0 (very positive)"
    )
    confidence: float = Field(
        description="Confidence in the score from 0.0 to 1.0"
    )
    label: str = Field(
        description="Sentiment label: 'positive', 'negative', or 'neutral'"
    )
    aspects: list[AspectSentiment] | None = Field(
        default=None, description="Aspect-level sentiment breakdown"
    )
    reasoning: str = Field(
        description="Brief explanation of the sentiment assessment"
    )


class AspectSentiment(BaseModel):
    """Sentiment for a specific aspect/topic mentioned in the text."""

    aspect: str = Field(description="The aspect or sub-topic")
    score: float = Field(description="Sentiment score for this aspect (-1.0 to 1.0)")
    label: str = Field(description="Sentiment label for this aspect")


# Fix forward reference - SentimentResult references AspectSentiment
SentimentResult.model_rebuild()


class ScoredItem(VerifiedItem):
    """A verified item with sentiment scores attached."""

    sentiment: SentimentResult
