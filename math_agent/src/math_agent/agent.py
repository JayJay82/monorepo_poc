from __future__ import annotations

import asyncio
import os

# ---------- A2A-SDK imports ---------------------------------------------------
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message
from agno.agent import Agent  # your business logic
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
from typing_extensions import override

from math_agent.math_tool import calcola  # ← tuo tool “calculate”

# -----------------------------------------------------------------------------


# 0.  dotenv / env -----------------------------------------------------------------
load_dotenv()
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:9999")
OPENAI_MODEL_ID = os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini")


# 1.  Business agent ----------------------------------------------------------------
math_agent = Agent(
    name="math_agent",
    tools=[calcola],
    model=OpenAIChat(id=OPENAI_MODEL_ID),
)


# 2.  AgentExecutor  (bridge A2A ⇆ your agent) --------------------------------------
class MathAgentExecutor(AgentExecutor):
    """Implements the two mandatory interface methods."""

    def __init__(self) -> None:
        self._agent = math_agent

    # message/send  or message/stream -------------------------------------------
    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Handle an incoming user message and enqueue a single reply."""
        user_text = context.message.content.text  # always plain text in this agent

        # Agno run is synchronous → delegate to a thread so we don't block the loop
        result = await asyncio.to_thread(self._agent.run, user_text)

        # result.content is an Agno ChatMessage; convert to plain str if needed
        event_queue.enqueue_event(new_agent_text_message(str(result.content)))

    # cancel (not supported in this simple agent) --------------------------------
    @override
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        raise UnsupportedOperationError()


# 3.  A2A metadata ------------------------------------------------------------------
skill = AgentSkill(
    id="calculate",
    name="Calculate Math Expression",
    description="Calculates any mathematical expression sent as input text.",
    tags=["math", "calculator"],
    examples=["2 + 2", "sin(3.14)"],
)

agent_card = AgentCard(
    name="Math Agent for Enterprise",
    description="A powerful math micro-service agent using Agno, OpenAI and A2A.",
    url=f"{PUBLIC_URL}/",  # exposed by `/.well-known/agent.json`
    version="2.0.0",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
)
