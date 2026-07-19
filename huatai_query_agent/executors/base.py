from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class QueryResult:
    success: bool
    columns: list[str]
    rows: list[tuple[Any, ...]]
    row_count: int
    preview_rows: list[tuple[Any, ...]]
    elapsed_ms: float
    error: str = ""

    def to_state(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "columns": self.columns,
            "rows": self.preview_rows,
            "row_count": self.row_count,
            "preview_rows": self.preview_rows,
            "elapsed_ms": self.elapsed_ms,
            "error": self.error,
        }


class SqlExecutor(Protocol):
    def execute(self, sql: str, *, preview_limit: int = 20) -> QueryResult:
        ...

