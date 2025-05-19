# Math Agent – Agno + OpenAI + A2A

**Math Agent** è un microservizio agentico Python che esegue operazioni matematiche tramite LLM e tool personalizzati, esposto tramite protocollo [A2A](https://github.com/google/A2A) per massima interoperabilità tra agenti.

---

## 🚀 Funzionalità

* Basato su [Agno](https://docs.agno.com/) per la definizione e l’orchestrazione di agenti AI
* Tool matematico custom collegato all’agente
* Supporto LLM OpenAI (`gpt-4o-mini` o altro)
* Esposto come servizio A2A conforme a [python-a2a](https://github.com/themanojdesai/python-a2a)
* Pronto per essere chiamato da altri agenti, orchestratori o API REST

---

## 📁 Struttura del progetto

```
math_agent/
├── pyproject.toml
├── .env                  # OpenAI API key qui
└── src/
    └── math_agent/
        ├── agent.py      # definizione agente
        ├── math_tool.py  # tool matematico
        └── a2a_server.py # server A2A python-a2a
```

---

## ⚙️ Setup

### 1. Clona il repository

```sh
git clone <your-repo-url>
cd math_agent
```

### 2. Installa le dipendenze con Poetry

```sh
poetry install
```

### 3. Configura le variabili d’ambiente

Crea un file `.env` nella root e aggiungi la tua chiave OpenAI:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
```

---

## ▶️ Avvio del server

```sh
poetry run python src/math_agent/a2a_server.py
```

Il server partirà su `http://localhost:8080`.

---

## 🔬 Test dell’agente (A2A Protocol)

### **Via curl**

```sh
curl -X POST http://localhost:8080/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"type":"text","text":"2+2*3"}, "role":"user"}'
```

### **Via Postman**

* Metodo: `POST`
* URL: `http://localhost:8080/a2a`
* Body (raw/JSON):

  ```json
  {
    "content": {
      "type": "text",
      "text": "2+2*3"
    },
    "role": "user"
  }
  ```

### **Risposta attesa**

```json
{
  "content": {
    "type": "text",
    "text": "8"
  },
  "role": "agent"
}
```

---

## 🛠️ Personalizzazione

* Modifica il tool matematico in `math_tool.py` per aggiungere funzioni o sicurezza.
* Cambia il modello OpenAI (es: `"gpt-4o-mini"`, `"gpt-4o"`, `"gpt-3.5-turbo"`, ecc) in `agent.py`.
* Aggiungi altri tool e aggiorna l’agente per servizi più complessi.

---

## 📄 Note

* **Compatibilità**: Testato con `python-a2a >=0.5.5`, `agno >=0.11.0`, `openai >=1.0.0`, Python 3.10+.
* **Sicurezza**: L’esempio usa `eval` solo per demo. In produzione usa parser matematici sicuri.

---

## 📚 Risorse

* [Agno Documentation](https://docs.agno.com/)
* [OpenAI API Reference](https://platform.openai.com/docs/)
* [A2A Protocol Spec](https://github.com/google/A2A)
* [python-a2a](https://github.com/themanojdesai/python-a2a)

---

## 🤝 License

MIT

---

## 🙋‍♂️ Supporto

Hai bisogno di aiuto o vuoi integrare il tuo Math Agent in un ecosistema più grande?
Apri una issue o contattami!
