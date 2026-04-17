"""API routes for topic management and analysis."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.sentiment_score import SentimentScore
from app.models.source_item import SourceItem
from app.models.topic import Topic
from app.services.analysis import run_analysis

router = APIRouter(prefix="/topics", tags=["topics"])


# --- Request / Response schemas ---


class TopicCreate(BaseModel):
    keyword: str


class TopicResponse(BaseModel):
    id: uuid.UUID
    keyword: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalyzeResponse(BaseModel):
    status: str
    topic_id: uuid.UUID


class AspectSentimentResponse(BaseModel):
    aspect: str
    score: float
    label: str


class SentimentScoreResponse(BaseModel):
    id: uuid.UUID
    overall_score: float
    confidence: float
    label: str
    aspects: list[AspectSentimentResponse] | None = None
    reasoning: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SourceItemResponse(BaseModel):
    id: uuid.UUID
    source: str
    title: str | None = None
    text: str
    author: str | None = None
    url: str | None = None
    published_at: datetime | None = None
    verified: bool
    sentiment_score: SentimentScoreResponse | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SentimentSummary(BaseModel):
    """Aggregated sentiment stats for a topic."""

    total_items: int
    positive_count: int
    negative_count: int
    neutral_count: int
    average_score: float | None = None
    average_confidence: float | None = None
    source_breakdown: dict[str, int]


class TopicDetailResponse(BaseModel):
    id: uuid.UUID
    keyword: str
    status: str
    created_at: datetime
    updated_at: datetime
    summary: SentimentSummary | None = None
    items: list[SourceItemResponse] = []

    model_config = {"from_attributes": True}


# --- Endpoints ---


@router.post("", response_model=TopicResponse, status_code=201)
async def create_topic(body: TopicCreate, db: AsyncSession = Depends(get_db)):
    """Create a new topic to track."""
    topic = Topic(keyword=body.keyword)
    db.add(topic)
    await db.flush()
    await db.refresh(topic)
    return topic


@router.get("", response_model=list[TopicResponse])
async def list_topics(db: AsyncSession = Depends(get_db)):
    """List all topics."""
    result = await db.execute(select(Topic).order_by(Topic.created_at.desc()))
    return result.scalars().all()


@router.get("/{topic_id}", response_model=TopicDetailResponse)
async def get_topic(topic_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a topic with full results including sentiment summary and scored items."""
    result = await db.execute(
        select(Topic)
        .where(Topic.id == topic_id)
        .options(
            selectinload(Topic.source_items).selectinload(SourceItem.sentiment_score),
        )
    )
    topic = result.scalar_one_or_none()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Build summary from scored items
    summary = await _build_summary(db, topic_id)

    return TopicDetailResponse(
        id=topic.id,
        keyword=topic.keyword,
        status=topic.status,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        summary=summary,
        items=[
            SourceItemResponse(
                id=item.id,
                source=item.source,
                title=item.title,
                text=item.text,
                author=item.author,
                url=item.url,
                published_at=item.published_at,
                verified=item.verified,
                sentiment_score=(
                    SentimentScoreResponse(
                        id=item.sentiment_score.id,
                        overall_score=item.sentiment_score.overall_score,
                        confidence=item.sentiment_score.confidence,
                        label=item.sentiment_score.label,
                        aspects=item.sentiment_score.aspects,
                        reasoning=item.sentiment_score.reasoning,
                        created_at=item.sentiment_score.created_at,
                    )
                    if item.sentiment_score
                    else None
                ),
                created_at=item.created_at,
            )
            for item in topic.source_items
        ],
    )


@router.post("/{topic_id}/analyze", response_model=AnalyzeResponse)
async def analyze_topic(
    topic_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger analysis for a topic.

    Kicks off the LangGraph pipeline as a background task so the
    API responds immediately. Poll GET /topics/{id} to check status.
    """
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    if topic.status == "running":
        raise HTTPException(status_code=409, detail="Analysis already running")

    topic.status = "running"
    # Commit explicitly so the background task sees the updated status
    # (don't rely on get_db cleanup ordering)
    await db.commit()

    background_tasks.add_task(run_analysis, topic.id)

    return AnalyzeResponse(status="started", topic_id=topic.id)


@router.delete("/{topic_id}", status_code=204)
async def delete_topic(topic_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a topic and all its associated data."""
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    await db.delete(topic)


# --- Helpers ---


async def _build_summary(db: AsyncSession, topic_id: uuid.UUID) -> SentimentSummary | None:
    """Build aggregated sentiment summary for a topic."""
    # Count items per label
    label_counts = await db.execute(
        select(SentimentScore.label, func.count(SentimentScore.id))
        .where(SentimentScore.topic_id == topic_id)
        .group_by(SentimentScore.label)
    )
    counts = {row[0]: row[1] for row in label_counts.all()}

    total = sum(counts.values())
    if total == 0:
        return None

    # Average score and confidence
    averages = await db.execute(
        select(
            func.avg(SentimentScore.overall_score),
            func.avg(SentimentScore.confidence),
        ).where(SentimentScore.topic_id == topic_id)
    )
    avg_row = averages.one()

    # Source breakdown
    source_counts = await db.execute(
        select(SourceItem.source, func.count(SourceItem.id))
        .where(SourceItem.topic_id == topic_id, SourceItem.verified.is_(True))
        .group_by(SourceItem.source)
    )
    source_breakdown = {row[0]: row[1] for row in source_counts.all()}

    return SentimentSummary(
        total_items=total,
        positive_count=counts.get("positive", 0),
        negative_count=counts.get("negative", 0),
        neutral_count=counts.get("neutral", 0),
        average_score=round(float(avg_row[0]), 4) if avg_row[0] is not None else None,
        average_confidence=round(float(avg_row[1]), 4) if avg_row[1] is not None else None,
        source_breakdown=source_breakdown,
    )
