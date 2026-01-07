# Reflektor — Structured Self-Reflection Exercise

A conversational AI assistant powered by LangChain that guides you through a CBT-style self-reflection exercise.

## What It Does

The assistant guides you through 8 steps:
1. **Situation** – What happened?
2. **Physical sensations** – What bodily sensations did you notice?
3. **Automatic thoughts** – What thoughts went through your mind?
4. **Emotions** – What emotions were present?
5. **Meaning/interpretation** – What did this mean to you?
6. **Alternative perspective** – Is there another possible interpretation?
7. **Next-step intention** (optional) – Is there a small next step you might take?
8. **Closure** – Final thoughts and summary

---

## Quick Start

### Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create `.env` file:**
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

3. **Start the backend server:**
```bash
python reflektor.py
```

Backend API: **http://localhost:8000**

### React Frontend (Optional)

1. **Install frontend dependencies:**
```bash
cd frontend
npm install
```

2. **Start the React app:**
```bash
npm run dev
```

Frontend UI: **http://localhost:3000**

> See `frontend/README.md` for detailed frontend documentation.

---

## API Usage

### Interactive Docs
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Quick Examples

**Health check:**
```bash
curl http://localhost:8000/health
```

**Create session:**
```bash
curl -X POST http://localhost:8000/sessions
```

**Submit response:**
```bash
curl -X POST http://localhost:8000/sessions/{session_id}/respond \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Your response here"}'
```

**Get history:**
```bash
curl http://localhost:8000/sessions/{session_id}/history
```

**End session:**
```bash
curl -X DELETE "http://localhost:8000/sessions/{session_id}?save=true"
```

### Python Example
```python
import requests

BASE_URL = "http://localhost:8000"

# Create session
response = requests.post(f"{BASE_URL}/sessions")
session = response.json()
session_id = session["session_id"]

print(session["assistant_response"])

# Submit response
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/respond",
    json={"user_input": "I had a difficult conversation."}
)
print(response.json()["assistant_response"])

# End and save
requests.delete(f"{BASE_URL}/sessions/{session_id}?save=true")
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions` | Create new session |
| POST | `/sessions/{id}/respond` | Submit response |
| GET | `/sessions/{id}` | Get session state |
| GET | `/sessions/{id}/history` | Get full history |
| DELETE | `/sessions/{id}?save={bool}` | End session |
| GET | `/health` | Health check |

---

## Optional: Phoenix Tracing

Start Phoenix for observability:
```bash
phoenix serve
```

Open http://localhost:6006 to see:
- LLM calls with prompts/responses
- Performance metrics
- Token usage and costs
- Error traces

---

## Development

**Auto-reload:**
```bash
uvicorn reflektor:app --reload
```

**Change port:**
```bash
uvicorn reflektor:app --port 8080
```

---

## Troubleshooting

**Cannot connect to API**
- Start server: `python reflektor.py`
- Check port 8000 is available

**OPENAI_API_KEY is not set**
- Create `.env` file with your API key

**Port already in use**
- Change port: `uvicorn reflektor:app --port 8080`

---

## Safety Note

This is **not a replacement for professional mental health care**. 

Crisis resources:
- Emergency: 911 (US)
- Crisis Text Line: Text HOME to 741741 (US)
- Suicide Prevention: 988 (US)

---

Happy reflecting! 🧘‍♀️✨
