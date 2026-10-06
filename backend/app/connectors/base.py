from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class SyncResult:
    """Standard result object returned by any connector sync operation."""

    success: bool = True
    items_created: int = 0
    items_updated: int = 0
    items_deleted: int = 0
    milestones_synced: int = 0
    dependencies_detected: int = 0
    errors: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    synced_at: Optional[datetime] = None


class BaseConnector(ABC):
    """Abstract base class defining the contract for all external data connectors."""

    def __init__(self, config: dict[str, Any]):
        self.config = config

    @abstractmethod
    async def connect(self) -> bool:
        """Validate credentials, repository access, or file accessibility.

        Returns True if connection succeeds, raises an exception or returns False otherwise.
        """
        pass

    @abstractmethod
    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Fetch external data, normalize records, and return SyncResult."""
        pass

    @abstractmethod
    async def status(self) -> dict[str, Any]:
        """Report connection health, rate limit status, and metadata."""
        pass

    async def disconnect(self) -> None:
        """Clean up open connections or file handles."""
        pass
