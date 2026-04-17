"""Bluesky aggregation agent using the public AT Protocol API.

Bluesky's public API requires no authentication for search,
making it the most accessible social media source.
"""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

from app.agents.schemas import RawSourceItem
from app.agents.sources.base import BaseSourceAgent
from app.core.config import settings

logger = logging.getLogger(__name__)


class BlueskyAgent(BaseSourceAgent):
    """Fetches posts from Bluesky matching a keyword via the public API."""

    name = "bluesky"

    async def fetch(self, keyword: str, max_items: int = 50) -> list[RawSourceItem]:
        items: list[RawSourceItem] = []
        base_url = settings.BLUESKY_API_URL.rstrip("/")
        limit = min(max_items, 100)

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{base_url}/xrpc/app.bsky.feed.searchPosts",
                params={
                    "q": keyword,
                    "limit": limit,
                    "sort": "latest",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        for post_wrapper in data.get("posts", []):
            record = post_wrapper.get("record", {})
            author_info = post_wrapper.get("author", {})
            text = record.get("text", "")

            if not text.strip():
                continue

            # Parse created_at timestamp
            published_at = None
            if record.get("createdAt"):
                try:
                    published_at = datetime.fromisoformat(
                        record["createdAt"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            # Build a Bluesky URL from the author handle and post rkey
            post_uri = post_wrapper.get("uri", "")
            handle = author_info.get("handle", "")
            rkey = post_uri.rsplit("/", 1)[-1] if "/" in post_uri else ""
            url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else None

            items.append(
                RawSourceItem(
                    source="bluesky",
                    external_id=post_uri or None,
                    title=None,  # Bluesky posts don't have titles
                    text=text,
                    author=author_info.get("displayName") or handle or None,
                    url=url,
                    published_at=published_at,
                    metadata={
                        "handle": handle,
                        "like_count": post_wrapper.get("likeCount", 0),
                        "repost_count": post_wrapper.get("repostCount", 0),
                        "reply_count": post_wrapper.get("replyCount", 0),
                    },
                )
            )

        return items
