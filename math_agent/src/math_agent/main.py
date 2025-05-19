# src/main.py
import os
from dotenv import load_dotenv
load_dotenv()

from agno.agent import Agent
from math_tool import calcola
from agno.models.openai import OpenAIChat

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
# Crea l'agente math_agent con il tool calcola
math_agent = Agent(
    name="math_agent",
    tools=[calcola],
    model=OpenAIChat(id="gpt4-0-mini")
)

# Espone via A2A REST (se vuoi fare un microservizio REST)
from python_a2a.server import A2AServer

if __name__ == "__main__":
    server = A2AServer(agent=math_agent)
    server.run(host="0.0.0.0", port=8080)