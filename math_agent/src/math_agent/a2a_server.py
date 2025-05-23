from __future__ import annotations

import os

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv

from math_agent.agent import MathAgentExecutor, agent_card

# -----------------------------------------------------------------------------


# 0.  dotenv / env -----------------------------------------------------------------
load_dotenv()
PORT = int(os.getenv("PORT", "9999"))


# 4.  Build Starlette + Uvicorn application ----------------------------------------
request_handler = DefaultRequestHandler(
    agent_executor=MathAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

app_builder = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
)

# 5.  Entrypoint --------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app_builder.build(), host="0.0.0.0", port=PORT)
