# Monorepo‑POC

> **Proof‑of‑Concept monorepo** built with Python 3.11+ and managed by **uv**. The workspace contains three internal packages:
>

> * `math_agent`   – LLM‑powered math agent, exposes **A2A Server**


---

## 1  Prerequisites

| Tool       | Version | Install once                                                           |
| ---------- | ------- | ---------------------------------------------------------------------- |
| **Python** |  ≥ 3.11 | [https://www.python.org/downloads/](https://www.python.org/downloads/) |
| **pipx**   |  ≥ 1.6  | `python -m pip install --user pipx` & `pipx ensurepath`                |
| **uv**     |  ≥ 0.2  | `pipx install uv`                                                      |

> On Windows re‑open PowerShell after `pipx ensurepath` so `%USERPROFILE%\.local\bin` is on *PATH*.

---

## 2  Cloning the repository

```bash
git clone https://github.com/JayJay82/monorepo_poc.git
cd monorepo_poc
```

---

## 3  Workspace Setup (one‑liner)

```bash
uv venv && uv sync --all-packages --group dev
```

* Creates `.venv/` in the repo root (ignored by Git).
* Installs **runtime + dev dependencies** for *every* member listed in `[tool.uv.workspace]`.
* Adds console scripts such as `a2a-server`, `black`, `ruff`, … inside `.venv/bin` / `Scripts`.

### Updating later

```bash
uv add fastapi                 # add dependency to current pkg
uv lock && uv sync             # regenerate lockfile & install
```

---

## 4  Global Dev Tooling

enable hooks uv run -- pre-commit install && uv run -- pre-commit install --hook-type commit-msg

| Task         | Command                                |
| ------------ | -------------------------------------- |
| Auto‑format  | `uv run -- black .`                    |
| Import‑sort  | `uv run -- isort .`                    |
| Lint (ruff)  | `uv run -- ruff check .`               |
| Commit hooks | `uv run -- pre-commit run --all-files` |

A shared configuration lives in **`pyproject.toml`** (root):

```toml
[tool.black]
line-length = 88

[tool.isort]
profile = "black"

[tool.flake8]
max-line-length = 88
```

---

## 5  Running the A2A Server

### Quick run (no activation needed)

```bash
uv run -- a2a-server  --port 8080   # or other CLI args
```

### Alternative forms

```bash
# via module import (keeps sys.path clean)
uv run -- python -m math_agent.a2a_server

# classic venv activation
source .venv/bin/activate && python src/math_agent/a2a_server.py
```

The server reads its configuration via environment variables; copy `.env.example` to `.env` and adjust as required.

---

## 6  Running Tests

```bash
uv run --pytest                 # run test suite in every package
# or per‑package
uv run --package math_agent -- pytest -q
```

---

## 7  Docker (optional deploy)

```Dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv pip sync . --package math_agent --group dev && uv cache prune
COPY math_agent/ ./math_agent
CMD ["uv","run","--","a2a-server"]
```

Build & run:

```bash
docker build -t a2a-server .
docker run -p 8080:8080 a2a-server
```

---


## 9  Troubleshooting & FAQ

| Issue                                             | Fix                                                     |
| ------------------------------------------------- | ------------------------------------------------------- |
| **“program not found”** after `uv run -- black .` |  Did you install the *dev* group? `uv sync --group dev` |
| uv lock fails with *package shadowing*            | Rename the local project (e.g. `mcp` → `mcp-local`).    |
| Need per‑project venvs                            | `uv venv --package a2a` then `uv sync --package a2a`.   |

---

Happy hacking!  Feel free to open issues or PRs.
