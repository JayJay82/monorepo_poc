# Monorepo Standards & Workflow

Questa guida descrive gli **standard di codifica** e il **workflow di sviluppo** centralizzati per tutti i micro‑progetti del repository.

---

## 📁 Struttura del Monorepo

```
monorepo-poc/
├── .pre-commit-config.yaml         # Hook di pre-commit condivisi
├── pyproject.toml                  # Configurazioni strumenti (Black, isort, Flake8, Commitizen)
├── dev-tools/                      # (opzionale) package con dev‑dependencies
├── a2a/
│   ├── pyproject.toml
│   └── src/...                     # Codice runtime del sub-progetto
├── math_agent/
│   ├── pyproject.toml
│   └── src/...
├── mcp/
│   ├── pyproject.toml
│   └── src/...
└── README.md                       # Questo file
```

## 🛠️ Configurazioni centralizzate

* **Black**: formattazione codice secondo PEP‑8
* **isort**: ordinamento import coerente con Black
* **Flake8**: linting per errori e stile
* **Commitizen**: enforcement Conventional Commits
* **pre-commit**: orchestratore dei hook sopra elencati

Tutti i file di configurazione (versioni e regole) risiedono nella root:

* `pyproject.toml` ➔ sezioni `[tool.black]`, `[tool.isort]`, `[tool.flake8]`, `[tool.commitizen]`
* `.pre-commit-config.yaml` ➔ definizione dei repo e dei hook

## 📦 Dipendenze di sviluppo

Ogni sub‑progetto (`a2a/`, `math_agent/`, `mcp/`, …) dichiara **solo** il gruppo "dev" per `pre-commit`:

```toml
[tool.poetry.group.dev]
optional    = false

[tool.poetry.group.dev.dependencies]
pre-commit = "^3.0"
```

Nessuna altra dev‑dependency è necessaria: i tool di lint/compliance vengono scaricati e isolati da pre‑commit.

## 🚀 Installazione

Per ciascun sub‑progetto, esegui:

```bash
cd <sub-progetto>
poetry install --with dev    # installa runtime + pre-commit
poetry run pre-commit install --install-hooks
```

> Se hai configurato Poetry per includere `dev` di default, `poetry install` basta.

---

## ⚙️ Uso Quotidiano

### Formattazione & Lint

* Esegui tutti gli hook su tutti i file:

  ```bash
  poetry run pre-commit run --all-files
  ```
* Oppure, al `git commit`, i hook partiranno automaticamente.

### Commit Convenzionali

* Il messaggio di commit viene validato dal hook `commitizen` secondo lo standard \[Conventional Commits].
* Per composizione interattiva:

  ```bash
  pipx install commitizen       # una tantum
  cd <sub-progetto>
  cz commit
  ```

---

## ➕ Aggiungere Nuovi Sub‑Progetti

Ecco come creare e configurare un nuovo sub‑progetto **tramite CLI di Poetry**, garantendo un virtualenv isolato e l’integrazione automatica degli hook:

1. **Dalla root del monorepo**, crea lo scheletro del progetto (sostituisci `<project-name>` con il nome desiderato, che sarà usato sia come directory che come nome del pacchetto):

   ```bash
   cd <path-to-monorepo>
   poetry new --src <project-name>
   ```

   Questo comando genererà:

   ```
   <project-name>/
   ├── pyproject.toml
   └── src/<project_name>/__init__.py
   ```

   Se desideri usare un nome pacchetto diverso dalla directory, aggiungi l'opzione `--name`:

   ````bash
   poetry new --src <project-name> --name <package_name>
   ```bash
   cd <path-to-monorepo>
   poetry new --src nuovo-progetto
   ````

   Questo comando genera:

   ```
   nuovo-progetto/
   ├── pyproject.toml
   └── src/nuovo_progetto/__init__.py
   ```

2. **Configura il gruppo `dev`** per gli hook in `nuovo-progetto/pyproject.toml`:

   ```bash
   cd nuovo-progetto
   poetry add --group dev --dev pre-commit
   ```

   Dopo il comando, in `pyproject.toml` troverai:

   ```toml
   [tool.poetry]
   name        = "nuovo-progetto"
   version     = "0.1.0"
   description = ""

   [tool.poetry.dependencies]
   python = "^3.10"

   [tool.poetry.group.dev]
   optional    = false
   description = "Dipendenze per il development"

   [tool.poetry.group.dev.dependencies]
   pre-commit = "^3.0"
   ```

3. **Installa runtime e dev-tools** (crea un venv dedicato):

   ```bash
   poetry install --with dev
   ```

   Questo comando:

   * crea un virtualenv separato per `nuovo-progetto`
   * installa le dipendenze di runtime e il gruppo `dev`

4. **Registra gli hook di pre-commit**:

   ```bash
   poetry run pre-commit install --install-hooks
   ```

5. **Verifica il setup**:

   ```bash
   poetry run pre-commit run --all-files
   ```

   oppure prova un normale `git commit` all’interno di `nuovo-progetto/`.

## 🔄 Aggiornamento delle dipendenze di sviluppo

Per aggiornare le versioni di Black, isort, Flake8 o Commitizen:

1. Modifica le rev in `.pre-commit-config.yaml` (repo e `rev:`).
2. Esegui nei sub-progetti:

   ```bash
   poetry run pre-commit autoupdate
   poetry run pre-commit install --install-hooks
   ```

---

## 🧪 Altri Strumenti

* **mypy**: tipizzazione statica
* **safety**: scansione vulnerabilità dipendenze

Puoi aggiungerli come hook in `.pre-commit-config.yaml` o come gruppi `dev` in `pyproject.toml`.

---

*Happy Coding!*

## 🐞 Risoluzione Problemi

Se i hook non partono automaticamente al `git commit`, segui questi passi:

1. Esegui dalla root del repository Git:

   ```bash
   poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg
   ```

   Dovresti vedere un messaggio come:

   ```
   pre-commit installed at /percorso/assoluto/.git/hooks/pre-commit
   ```
2. Verifica che i file `.git/hooks/pre-commit` e `.git/hooks/commit-msg` esistano ed siano eseguibili.
3. Conferma l'installazione eseguendo:

   ```bash
   poetry run pre-commit run --all-files
   ```

   oppure prova un normale `git commit`.
4. Ricorda che i hook funzionano anche se sei in una sotto-cartella, purché il file `.git` sia nella root del monorepo.

Dopo questi passaggi, i tuoi hook (Black, isort, Flake8 e Commitizen) verranno eseguiti automaticamente a ogni commit.
