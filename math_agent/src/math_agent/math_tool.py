# src/math_tools.py
from agno.tools import tool

@tool
def calcola(expression: str) -> str:
    """Esegue il calcolo matematico dell'espressione fornita come stringa. Usa solo per operazioni matematiche."""
    try:
        # eval con restrizioni minime di sicurezza
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Errore: {str(e)}"