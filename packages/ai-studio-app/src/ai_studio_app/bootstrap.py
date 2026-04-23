from ai_studio_ext import (
    EchoAgentRuntime,
    NoopKnowledgeGateway,
    NoopMemoryGateway,
    NoopToolGateway,
)
from ai_studio_serve import RunService


def create_default_run_service() -> RunService:
    runtime = EchoAgentRuntime(
        memory=NoopMemoryGateway(),
        knowledge=NoopKnowledgeGateway(),
        tools=NoopToolGateway(),
    )
    return RunService(runtime)
