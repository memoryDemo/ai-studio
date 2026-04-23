from ai_studio_core import (
    KnowledgeGateway,
    MemoryGateway,
    RunContext,
    RunRequest,
    RunResult,
    ToolGateway,
)


class EchoAgentRuntime:
    def __init__(
        self,
        *,
        memory: MemoryGateway,
        knowledge: KnowledgeGateway,
        tools: ToolGateway,
    ) -> None:
        self._memory = memory
        self._knowledge = knowledge
        self._tools = tools

    async def run(self, *, request: RunRequest, context: RunContext) -> RunResult:
        memory_hits = await self._memory.load_working_set(
            thread_id=request.thread_id,
            query=request.input,
        )
        await self._memory.remember_episode(
            run_id=context.run_id,
            content=request.input,
            metadata=request.metadata,
        )
        return RunResult(
            output=f"[{context.run_id}] {request.input}",
            memory_hits=memory_hits,
            metadata={
                "runtime": "echo",
                "thread_id": request.thread_id,
            },
        )
