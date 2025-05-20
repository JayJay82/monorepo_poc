import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request

from math_agent.agent import math_agent

app = FastAPI()


@app.post("/calcola")
async def calcola_api(request: Request):
    data = await request.json()
    expr = data.get("expression")
    prompt = f"Calcola questa espressione matematica: {expr}"
    result = math_agent.run(prompt)
    return {"result": result.content}
