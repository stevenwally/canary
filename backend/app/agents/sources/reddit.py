"""Reddit aggregation agent using asyncpraw."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import asyncpraw

from app.agents.schemas import RawSourceItem
from app.agents.sources.base import BaseSourceAgent
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedditAgent(BaseSourceAgent):
    """Fetches posts and comments from Reddit matching a keyword."""

    name = "reddit"

    async def fetch(self, keyword: str, max_items: int = 50) -> list[RawSourceItem]:
        if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
            logger.warning("Reddit credentials not configured, skipping")
            return []

        items: list[RawSourceItem] = []

        async with asyncpraw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
        ) as reddit:
            # Search across all subreddits, sorted by relevance
            subreddit = await reddit.subreddit("all")
            async for submission in subreddit.search(
                keyword, sort="relevance", time_filter="week", limit=max_items
            ):
                # Combine title and selftext for full context
                text_parts = [submission.title]
                if submission.selftext:
                    text_parts.append(submission.selftext)
                text = "\n\n".join(text_parts)

                items.append(
                    RawSourceItem(
                        source="reddit",
                        external_id=submission.id,
                        title=submission.title,
                        text=text,
                        author=str(submission.author) if submission.author else None,
                        url=f"https://reddit.com{submission.permalink}",
                        published_at=datetime.fromtimestamp(
                            submission.created_utc, tz=UTC
                        ),
                        metadata={
                            "subreddit": str(submission.subreddit),
                            "score": submission.score,
                            "num_comments": submission.num_comments,
                            "upvote_ratio": submission.upvote_ratio,
                        },
                    )
                )

        return items
