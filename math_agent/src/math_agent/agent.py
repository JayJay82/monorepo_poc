import os

from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from python_a2a import A2AServer, Message, MessageRole, TextContent

from math_agent.math_tool import calcola

# Crea l'agente math_agent con il tool calcola
math_agent = Agent(
    name="math_agent", tools=[calcola], model=OpenAIChat(id="gpt-4o-mini")
)


class MathAgentServer(A2AServer):
    def handle_message(self, message):
        if message.content.type == "text":
            user_input = message.content.text
            response_text = math_agent.run(user_input)
            return Message(
                content=TextContent(text=response_text.content),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id,
            )


agent_card = {
    "name": "Math Agent for Enterprise",
    "description": "A powerful math microservice agent using Agno, OpenAI, and A2A.",
    "version": "2.0.0",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False,
        "google_a2a_compatible": True,
        "parts_array_format": True,
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "name": "Calculate Math Expression",
            "description": "Calculates any mathematical expression sent as input text.",
            "input": "text",
            "output": "text",
        }
    ],
}
