"""NewsAPI aggregation agent."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import httpx

from app.agents.schemas import RawSourceItem
from app.agents.sources.base import BaseSourceAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

NEWSAPI_SEARCH_URL = "https://newsapi.org/v2/everything"


class NewsAPIAgent(BaseSourceAgent):
    """Fetches news articles from NewsAPI matching a keyword."""

    name = "newsapi"

    async def fetch(self, keyword: str, max_items: int = 50) -> list[RawSourceItem]:
        if not settings.NEWSAPI_KEY:
            logger.warning("NewsAPI key not configured, skipping")
            return []

        items: list[RawSourceItem] = []
        page_size = min(max_items, 100)  # NewsAPI max per page

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                NEWSAPI_SEARCH_URL,
                params={
                    "q": keyword,
                    "sortBy": "relevancy",
                    "pageSize": page_size,
                    "language": "en",
                    "apiKey": settings.NEWSAPI_KEY,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("status") != "ok":
            logger.error("NewsAPI error: %s", data.get("message", "unknown"))
            return []

        for article in data.get("articles", []):
            # Combine title + description + content for full text
            text_parts = []
            if article.get("title"):
                text_parts.append(article["title"])
            if article.get("description"):
                text_parts.append(article["description"])
            if article.get("content"):
                text_parts.append(article["content"])
            text = "\n\n".join(text_parts)

            if not text.strip():
                continue

            published_at = None
            if article.get("publishedAt"):
                try:
                    published_at = datetime.fromisoformat(
                        article["publishedAt"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            items.append(
                RawSourceItem(
                    source="newsapi",
                    external_id=article.get("url"),
                    title=article.get("title"),
                    text=text,
                    author=article.get("author"),
                    url=article.get("url"),
                    published_at=published_at,
                    metadata={
                        "source_name": article.get("source", {}).get("name"),
                        "image_url": article.get("urlToImage"),
                    },
                )
            )

        return items
