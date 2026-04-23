from typing import Any, Protocol

from ai_studio_core.contracts.models import RetrievedItem, ToolCall, ToolResult


class MemoryGateway(Protocol):
    async def load_working_set(
        self, *, thread_id: str, query: str
    ) -> list[RetrievedItem]: ...

    async def remember_episode(
        self, *, run_id: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None: ...


class KnowledgeGateway(Protocol):
    async def search(self, *, query: str, top_k: int = 5) -> list[RetrievedItem]: ...


class ToolGateway(Protocol):
    async def invoke(self, call: ToolCall) -> ToolResult: ...
