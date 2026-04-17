"""Analysis service - runs the pipeline and persists results to the database."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import pipeline
from app.agents.schemas import SentimentResult, VerifiedItem
from app.core.database import async_session
from app.models.sentiment_score import SentimentScore
from app.models.source_item import SourceItem
from app.models.topic import Topic

logger = logging.getLogger(__name__)


async def run_analysis(topic_id: uuid.UUID) -> None:
    """Run the full analysis pipeline for a topic and persist results.

    This is designed to be called from a background task so it
    manages its own database session.

    Args:
        topic_id: The UUID of the topic to analyze.
    """
    async with async_session() as db:
        try:
            # Load the topic
            result = await db.execute(select(Topic).where(Topic.id == topic_id))
            topic = result.scalar_one_or_none()
            if topic is None:
                logger.error("Topic %s not found", topic_id)
                return

            topic.status = "running"
            await db.commit()

            # Run the LangGraph pipeline
            logger.info("Starting analysis pipeline for topic '%s'", topic.keyword)
            state = await pipeline.ainvoke(
                {
                    "topic": topic.keyword,
                    "topic_id": str(topic_id),
                    "source_items": [],
                    "verified_items": [],
                    "scores": [],
                    "status": "started",
                }
            )

            # Persist results
            verified_items = state.get("verified_items", [])
            scores = state.get("scores", [])

            logger.info(
                "Pipeline complete: %d verified items, %d scores",
                len(verified_items),
                len(scores),
            )

            await _persist_results(db, topic_id, verified_items, scores)

            # Mark topic as completed
            topic.status = "completed"
            await db.commit()

            logger.info("Analysis complete for topic '%s'", topic.keyword)

        except Exception:
            logger.exception("Analysis failed for topic %s", topic_id)
            # Try to mark topic as failed
            try:
                topic.status = "failed"
                await db.commit()
            except Exception:
                logger.exception("Failed to update topic status to 'failed'")
                await db.rollback()


async def _persist_results(
    db: AsyncSession,
    topic_id: uuid.UUID,
    verified_items: list[dict],
    scores: list[dict],
) -> None:
    """Persist verified items and their sentiment scores to the database."""
    for i, item_data in enumerate(verified_items):
        verified = VerifiedItem(**item_data)

        # Create the SourceItem record
        source_item = SourceItem(
            topic_id=topic_id,
            source=verified.source,
            external_id=verified.external_id,
            title=verified.title,
            text=verified.text,
            author=verified.author,
            url=verified.url,
            published_at=verified.published_at,
            metadata_=verified.metadata,
            verified=True,
        )
        db.add(source_item)
        await db.flush()  # Get the generated ID

        # Create the SentimentScore record if we have a score for this item
        if i < len(scores):
            score_data = scores[i]
            sentiment = SentimentResult(**score_data)

            # Serialize aspects to plain dicts for the JSON column
            aspects_data = None
            if sentiment.aspects:
                aspects_data = [a.model_dump() if hasattr(a, 'model_dump') else a for a in sentiment.aspects]

            sentiment_score = SentimentScore(
                source_item_id=source_item.id,
                topic_id=topic_id,
                overall_score=sentiment.overall_score,
                confidence=sentiment.confidence,
                label=sentiment.label,
                aspects=aspects_data,
                reasoning=sentiment.reasoning,
            )
            db.add(sentiment_score)

    await db.flush()
