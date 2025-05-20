from python_a2a import run_server

from math_agent.agent import MathAgentServer, agent_card

# Crea l'agente math_agent con il tool calcola


if __name__ == "__main__":
    agent = MathAgentServer()
    agent.agent_card = agent_card
    run_server(agent, host="0.0.0.0", port=8080)
