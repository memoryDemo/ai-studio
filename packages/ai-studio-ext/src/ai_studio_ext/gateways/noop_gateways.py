from typing import Any

from ai_studio_core import RetrievedItem, ToolCall, ToolResult


class NoopMemoryGateway:
    async def load_working_set(
        self, *, thread_id: str, query: str
    ) -> list[RetrievedItem]:
        return []

    async def remember_episode(
        self, *, run_id: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        return None


class NoopKnowledgeGateway:
    async def search(self, *, query: str, top_k: int = 5) -> list[RetrievedItem]:
        return []


class NoopToolGateway:
    async def invoke(self, call: ToolCall) -> ToolResult:
        return ToolResult(
            name=call.name,
            content="Tool execution is not wired yet.",
        )
