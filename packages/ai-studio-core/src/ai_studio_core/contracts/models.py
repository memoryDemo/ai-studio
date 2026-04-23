from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RunRequest:
    thread_id: str
    input: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RunContext:
    run_id: str
    thread_id: str
    user_id: str | None = None
    workspace_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievedItem:
    id: str
    content: str
    score: float | None = None
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ToolResult:
    name: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RunResult:
    output: str
    memory_hits: list[RetrievedItem] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
