from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .models import DealerSource, RawListing


class Collector(ABC):
    def __init__(self, source: DealerSource, workspace_root: Path) -> None:
        self.source = source
        self.workspace_root = workspace_root

    @abstractmethod
    def collect(self) -> list[RawListing]:
        """Return raw listings from one source without scoring or guessing missing fields."""
