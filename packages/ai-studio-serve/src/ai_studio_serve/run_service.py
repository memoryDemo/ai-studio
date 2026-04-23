from ai_studio_core import AgentRuntime, RunContext, RunRequest, RunResult


class RunService:
    def __init__(self, runtime: AgentRuntime) -> None:
        self._runtime = runtime

    async def create_run(
        self, *, request: RunRequest, context: RunContext
    ) -> RunResult:
        return await self._runtime.run(request=request, context=context)
