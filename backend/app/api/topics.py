"""API routes for topic management and analysis."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
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
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class AnalyzeResponse(BaseModel):
    status: str
    topic_id: uuid.UUID


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


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a single topic by ID."""
    result = await db.execute(
        select(Topic)
        .where(Topic.id == topic_id)
        .options(
            selectinload(Topic.source_items),
            selectinload(Topic.sentiment_scores),
        )
    )
    topic = result.scalar_one_or_none()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


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
    await db.flush()

    # Run the pipeline in the background
    background_tasks.add_task(run_analysis, topic.id)

    return AnalyzeResponse(status="started", topic_id=topic.id)
