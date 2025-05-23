# Math Agent – A2A Micro‑service

A micro‑service that evaluates mathematical expressions via **Agno + OpenAI** and exposes an [A2A](https://github.com/google/a2a-python) JSON‑RPC interface.

* **Language** : Python ≥ 3.11
* **Runtime**  : [`a2a-sdk`](https://pypi.org/project/a2a-sdk/) + [`uvicorn`](https://www.uvicorn.org/)
* **Workspace**: Managed by [`uv`](https://github.com/astral-sh/uv) in the parent monorepo

---

## 1  Quick Start

```bash
# clone the monorepo and enter it
$ git clone https://github.com/JayJay82/monorepo_poc.git
$ cd monorepo_poc

# create the workspace venv + install only this package (and dev deps)
$ uv venv && uv sync --package math_agent --group dev

# copy example env and set your OpenAI key
$ cp math_agent/.env.example math_agent/.env
$ editor math_agent/.env            # edit PORT, PUBLIC_URL, OPENAI_API_KEY …

# run the server (default PORT 9999)
$ uv run -- python -m math_agent.a2a_server
```

Navigate to [http://localhost:9999/.well-known/agent.json](http://localhost:9999/.well-known/agent.json) to see the **Agent Card**, then send a JSON‑RPC request to `/`.

---

## 2  Environment Variables

| Var               | Default                 | Required | Description                          |
| ----------------- | ----------------------- | -------- | ------------------------------------ |
| `OPENAI_API_KEY`  | –                       | **Yes**  | Your OpenAI API key.                 |
| `OPENAI_MODEL_ID` | `gpt-4o-mini`           | No       | Model used by Agno.                  |
| `PORT`            | `9999`                  | No       | HTTP port.                           |
| `PUBLIC_URL`      | `http://localhost:9999` | No       | Public URL announced in `AgentCard`. |

Put them in `math_agent/.env`; they are loaded automatically by `dotenv`.

---

## 3  API Endpoints

| Method   | Path                      | Notes                                                                  |
| -------- | ------------------------- | ---------------------------------------------------------------------- |
| **GET**  | `/.well-known/agent.json` | Agent metadata (name, skills, capabilities…).                          |
| **POST** | `/`                       | JSON‑RPC requests (`message/send`, `message/stream`, `tasks/send`, …). |

### Example request (message/send)

```bash
curl -X POST http://localhost:9999/ \
     -H "Content-Type: application/json" \
     -d '{
           "jsonrpc": "2.0",
           "id": 1,
           "method": "message/send",
           "params": {
             "message": {
               "kind": "message",
               "role": "user",
               "content": {"type": "text", "text": "2+2"}
             }
           }
         }'
```

Expected response (simplified):

```json
{"jsonrpc":"2.0","id":1,"result":{"events":[{"kind":"message","role":"agent","content":{"type":"text","text":"4"}}]}}
```

---

## 4  Project Layout

```
math_agent/
├─ math_agent/
│  ├─ __init__.py
│  ├─ a2a_server.py      # <‑ entry‑point (Starlette + A2A SDK)
│  └─ math_tool.py       # "calcola" tool consumed by Agno
├─ tests/
├─ pyproject.toml        # package metadata & deps
└─ README.md             # this file
```

---

## 5  Development Tasks

| Task                     | Command                        |
| ------------------------ | ------------------------------ |
| **Format**               | `uv run -- black .`            |
| **Import sort**          | `uv run -- isort .`            |
| **Lint**                 | `uv run -- ruff check .`       |
| **Tests**                | `uv run --pytest -q`           |
| **Pre‑commit** (install) | `uv run -- pre-commit install` |

> All tooling is configured in the monorepo root `pyproject.toml`; run commands from the root or pass `--config ../../pyproject.toml`.

---

## 6  Docker (optional)

```dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv pip sync . --package math_agent && uv cache prune

COPY math_agent/ ./math_agent
EXPOSE 9999
CMD ["uv", "run", "--", "python", "-m", "math_agent.a2a_server"]
```

Build & run:

```bash
docker build -t math-agent .
docker run -p 9999:9999 math-agent
```

---

## 7  Troubleshooting

| Issue                             | Fix                                                   |
| --------------------------------- | ----------------------------------------------------- |
| 404 on `/a2a`                     | Use `/` (root) for JSON‑RPC.                          |
| 405 on `GET /`                    | Only **POST** is allowed on `/`.                      |
| Import errors in PyCharm          | Set interpreter to `monorepo_poc/.venv/…`.            |
| Hardlink warning during `uv sync` | `set UV_LINK_MODE=copy` (Windows) or see root README. |

---

## License

Apache 2.0 – see [LICENSE](../LICENSE).
