from typing import Protocol

from ai_studio_core.contracts.models import RunContext, RunRequest, RunResult


class AgentRuntime(Protocol):
    async def run(self, *, request: RunRequest, context: RunContext) -> RunResult: ...
