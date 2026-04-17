"""Base class for all source aggregation agents."""

from __future__ import annotations

import abc
import logging

from app.agents.schemas import RawSourceItem

logger = logging.getLogger(__name__)


class BaseSourceAgent(abc.ABC):
    """Abstract base for source aggregation agents.

    Each concrete agent knows how to fetch data from one platform
    and normalize it into RawSourceItem objects.
    """

    name: str = "base"

    @abc.abstractmethod
    async def fetch(self, keyword: str, max_items: int = 50) -> list[RawSourceItem]:
        """Fetch items matching the keyword from this source.

        Args:
            keyword: The search term/topic.
            max_items: Maximum number of items to return.

        Returns:
            List of normalized RawSourceItem objects.
        """
        ...

    async def safe_fetch(self, keyword: str, max_items: int = 50) -> list[RawSourceItem]:
        """Fetch with error handling. Returns empty list on failure."""
        try:
            items = await self.fetch(keyword, max_items)
            logger.info("%s: fetched %d items for '%s'", self.name, len(items), keyword)
            return items
        except Exception:
            logger.exception("%s: failed to fetch for '%s'", self.name, keyword)
            return []
