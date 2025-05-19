import os
from dotenv import load_dotenv
load_dotenv()

from python_a2a import A2AServer, Message, TextContent, MessageRole
from agno.agent import Agent
from math_agent.math_tool import calcola
from agno.models.openai import OpenAIChat


# Crea l'agente math_agent con il tool calcola
math_agent = Agent(
    name="math_agent",
    tools=[calcola],
    model=OpenAIChat(id="gpt-4o-mini")
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
                conversation_id=message.conversation_id
            )