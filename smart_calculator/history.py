"""History module: CRUD operations with optional JSON persistence."""
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .exceptions import HistoryError
from .logger import get_logger

log = get_logger("history")


@dataclass
class HistoryEntry:
    id: int
    expression: str
    result: str
    timestamp: str


class History:
    """Stores past calculations. Pass ``path`` to persist between runs."""

    def __init__(self, path: Optional[os.PathLike] = None, max_entries: int = 500):
        self.path = Path(path) if path else None
        self.max_entries = max_entries
        self._entries: List[HistoryEntry] = []
        self._next_id = 1
        if self.path:
            self._load()

    # Create
    def add(self, expression: str, result: str) -> HistoryEntry:
        entry = HistoryEntry(self._next_id, expression, result,
                             datetime.now().isoformat(timespec="seconds"))
        self._next_id += 1
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]
        self._save()
        return entry

    # Read
    def all(self, limit: Optional[int] = None) -> List[HistoryEntry]:
        return list(self._entries[-limit:] if limit else self._entries)

    def get(self, entry_id: int) -> HistoryEntry:
        for e in self._entries:
            if e.id == entry_id:
                return e
        raise HistoryError(f"No history entry with id {entry_id}")

    def search(self, text: str) -> List[HistoryEntry]:
        text = text.lower()
        return [e for e in self._entries if text in e.expression.lower() or text in e.result.lower()]

    # Delete
    def delete(self, entry_id: int) -> None:
        entry = self.get(entry_id)
        self._entries.remove(entry)
        self._save()

    def clear(self) -> None:
        self._entries.clear()
        self._save()

    def __len__(self) -> int:
        return len(self._entries)

    # Persistence (atomic write so a crash cannot corrupt the file)
    def _save(self) -> None:
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump([asdict(e) for e in self._entries], fh, indent=2)
            os.replace(tmp, self.path)
        except OSError as exc:
            log.warning("Could not save history: %s", exc)

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._entries = [HistoryEntry(**item) for item in data][-self.max_entries:]
            self._next_id = max((e.id for e in self._entries), default=0) + 1
        except (OSError, ValueError, TypeError, KeyError) as exc:
            log.warning("History file unreadable, starting fresh: %s", exc)
            self._entries = []
