"""
Structured self-reflection exercise (CBT-style) — Reflektor REST API

This FastAPI application provides a REST API for the structured self-reflection exercise.
Each session is managed independently with a unique session ID.

API Endpoints:
- POST /sessions - Create a new reflection session
- POST /sessions/{session_id}/respond - Submit a user response
- GET /sessions/{session_id} - Get current session state
- GET /sessions/{session_id}/history - Get full session history
- DELETE /sessions/{session_id} - End and optionally save a session
"""

import os
import uuid
import json
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

# OpenInference instrumentation for Phoenix Arize
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

load_dotenv(override=True)

# Constants
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
DEFAULT_TEMPERATURE = 0.4
DEFAULT_MAX_TOKENS = 500


def env_flag(name: str, default: bool = False) -> bool:
    """Parse boolean-like environment variables safely."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

# System prompt and steps (same as CLI version)
SYSTEM_PROMPT = """
You are a structured, safe self-reflection assistant. Your task is to guide the user, step-by-step, through a CBT-style self-reflection exercise about a specific situation. Strictly follow the rules below:

- Ask only one question at a time and wait for the user's answer before proceeding.
- Do not give advice, do not propose solutions, do not judge, and do not make diagnoses.
- Keep a compassionate, neutral, and non-directive tone.
- If the user indicates immediate danger (e.g., self-harm, abuse), ask about safety in a calm way and recommend contacting local emergency services or a crisis line — do not provide therapeutic instructions.

Follow these exercise steps in order (allow the user to skip any step they prefer not to answer):
1) Situation — "What happened?" (ask for a short, concrete description)
2) Physical sensations — "What bodily sensations did you notice?"
3) Automatic thoughts — "What thoughts went through your mind?"
4) Emotions — "What emotions were present?"
5) Meaning / interpretation — "What did this mean to you?"
6) Alternative perspective — "Can you see another possible interpretation?"
7) Next-step intention (optional) — "Is there a small next step you might take?"
8) Closure — brief summary, closing and thank you

After each user answer:
- Provide a brief, empathetic acknowledgment of their answer (1-2 sentences)
- Only move to the next step when the user's answer addresses the current step
- If their answer is off-topic or unclear, gently guide them back to the current question
- When ready to advance to the next step, include the marker [ADVANCE] at the very end of your response
- Do not include [ADVANCE] if the user hasn't adequately addressed the current step yet

Always follow the rules: do not diagnose, do not give therapy, and ask only one question at a time.
"""

STEPS = [
    {"id": 1, "title": "Situation", "question": "Briefly: what happened? Please describe a specific situation."},
    {"id": 2, "title": "Physical sensations", "question": "What physical sensations did you notice in that situation? (e.g., tightness in chest, sweating, tension)"},
    {"id": 3, "title": "Automatic thoughts", "question": "What thoughts ran through your mind during the situation?"},
    {"id": 4, "title": "Emotions", "question": "What emotions were present? Name them briefly."},
    {"id": 5, "title": "Meaning / interpretation", "question": "What did this mean to you? What interpretation did you give to the events?"},
    {"id": 6, "title": "Alternative perspective", "question": "Can you identify another possible interpretation of the situation? (Try to name at least one alternative)"},
    {"id": 7, "title": "Next-step intention (optional)", "question": "Is there a small next step you might take related to this situation? (optional)"},
    {"id": 8, "title": "Closure", "question": "Briefly: is there anything else you want to add before we finish the exercise?"}
]


# Pydantic models for API requests/responses
class SessionCreateResponse(BaseModel):
    session_id: str
    message: str
    current_step: int
    step_title: str
    assistant_response: str


class UserResponse(BaseModel):
    user_input: str


class SessionResponse(BaseModel):
    session_id: str
    current_step: int
    step_title: str
    total_steps: int
    is_complete: bool
    assistant_response: str


class HistoryItem(BaseModel):
    step_id: int
    title: str
    question: str
    answer: str
    assistant: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    history: List[HistoryItem]
    is_complete: bool


class SessionEndResponse(BaseModel):
    session_id: str
    message: str
    saved_path: Optional[str] = None


# Session management
@dataclass
class ReflectionSession:
    """Manages a single reflection session state."""
    session_id: str
    chain: any
    message_history: ChatMessageHistory
    current_step_index: int
    history: List[Dict]
    is_complete: bool
    created_at: datetime.datetime


class SessionManager:
    """Manages multiple reflection sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, ReflectionSession] = {}
    
    def create_session(self) -> ReflectionSession:
        """Create a new reflection session."""
        session_id = str(uuid.uuid4())

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY is missing. Add it to the .env file."
            )
        if api_key.lower().endswith(".txt") or "\\" in api_key:
            raise HTTPException(
                status_code=500,
                detail=(
                    "OPENAI_API_KEY appears to be a file path, not an API key. "
                    "Set OPENAI_API_KEY in .env to a real key value."
                )
            )
        
        # Create LangChain components
        llm = ChatOpenAI(
            api_key=api_key,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        chain = prompt | llm
        message_history = ChatMessageHistory()
        
        session = ReflectionSession(
            session_id=session_id,
            chain=chain,
            message_history=message_history,
            current_step_index=0,
            history=[],
            is_complete=False,
            created_at=datetime.datetime.now()
        )
        
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> ReflectionSession:
        """Get an existing session or raise error."""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return self.sessions[session_id]
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Initialize FastAPI app and session manager
app = FastAPI(
    root_path="/api",
    description="Structured self-reflection exercise (CBT-style) REST API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    
        "https://api.navigate.hu",
        "https://reflector-app-inky.vercel.app/",
        "http://localhost:5173",


 ],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager()


# Setup tracing
def setup_tracing(endpoint="http://127.0.0.1:6006/v1/traces"):
    """Setup OpenInference tracing for Phoenix."""
    tracer_provider = trace_sdk.TracerProvider()
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
    )
    trace_api.set_tracer_provider(tracer_provider)
    LangChainInstrumentor().instrument()
    print(f"✓ Phoenix tracing enabled at {endpoint}")


@app.on_event("startup")
async def startup_event():
    """Initialize tracing on startup."""
    if not env_flag("ENABLE_PHOENIX_TRACING", default=False):
        print("Phoenix tracing disabled (set ENABLE_PHOENIX_TRACING=true to enable).")
        return

    try:
        phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006/v1/traces")
        setup_tracing(phoenix_endpoint)
    except Exception as e:
        print(f"Warning: Could not enable Phoenix tracing: {e}")


# API Endpoints
@app.post("/sessions", response_model=SessionCreateResponse)
async def create_session():
    """Create a new reflection session and get the first question."""
    session = session_manager.create_session()
    
    # Get initial response from assistant
    initial_input = f"Please start the reflection exercise. We're beginning with step 1: {STEPS[0]['title']} - {STEPS[0]['question']}"
    
    try:
        response = session.chain.invoke({
            "history": session.message_history.messages,
            "input": initial_input
        })
        
        session.message_history.add_user_message(initial_input)
        session.message_history.add_ai_message(response.content)
        
        return SessionCreateResponse(
            session_id=session.session_id,
            message="Session created successfully",
            current_step=1,
            step_title=STEPS[0]['title'],
            assistant_response=response.content
        )
    except Exception as e:
        session_manager.delete_session(session.session_id)
        raise HTTPException(status_code=500, detail=f"Error initializing session: {str(e)}")


@app.post("/sessions/{session_id}/respond", response_model=SessionResponse)
async def submit_response(session_id: str, user_response: UserResponse):
    """Submit a user response and get the next question."""
    session = session_manager.get_session(session_id)
    
    if session.is_complete:
        raise HTTPException(status_code=400, detail="Session is already complete")
    
    user_input = user_response.user_input.strip()
    
    if not user_input:
        raise HTTPException(status_code=400, detail="User input cannot be empty")
    
    # Current step information
    current_step = STEPS[session.current_step_index]
    is_last_step = (session.current_step_index == len(STEPS) - 1)
    
    # Build context instruction
    if is_last_step:
        step_context = f"This is the final step ({current_step['title']}). After acknowledging their answer, provide a warm closure and summary. Include [ADVANCE] to mark completion."
    else:
        next_step = STEPS[session.current_step_index + 1]
        step_context = f"Current step: {current_step['title']}. If their answer addresses this step, acknowledge and move to step {next_step['id']}: {next_step['title']} - {next_step['question']}. Include [ADVANCE] when moving forward."
    
    user_input_with_context = f"{user_input}\n\n[Step context: {step_context}]"
    
    try:
        # Get assistant response
        response = session.chain.invoke({
            "history": session.message_history.messages,
            "input": user_input_with_context
        })
        
        assistant_response = response.content
        should_advance = "[ADVANCE]" in assistant_response
        assistant_response_clean = assistant_response.replace("[ADVANCE]", "").strip()
        
        # Update message history
        session.message_history.add_user_message(user_input)
        session.message_history.add_ai_message(assistant_response_clean)
        
        # Save to history
        session.history.append({
            "step_id": current_step['id'],
            "title": current_step['title'],
            "question": current_step['question'],
            "answer": user_input,
            "assistant": assistant_response_clean
        })
        
        # Advance step if needed
        if should_advance and not is_last_step:
            session.current_step_index += 1
        
        # Mark complete if last step and should advance
        if is_last_step and should_advance:
            session.is_complete = True
        
        current_step_info = STEPS[session.current_step_index]
        
        return SessionResponse(
            session_id=session.session_id,
            current_step=session.current_step_index + 1,
            step_title=current_step_info['title'],
            total_steps=len(STEPS),
            is_complete=session.is_complete,
            assistant_response=assistant_response_clean
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing response: {str(e)}")


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session_state(session_id: str):
    """Get the current state of a session."""
    session = session_manager.get_session(session_id)
    current_step = STEPS[session.current_step_index]
    
    # Get last assistant message
    last_message = ""
    if session.message_history.messages:
        for msg in reversed(session.message_history.messages):
            if hasattr(msg, 'type') and msg.type == 'ai':
                last_message = msg.content
                break
    
    return SessionResponse(
        session_id=session.session_id,
        current_step=session.current_step_index + 1,
        step_title=current_step['title'],
        total_steps=len(STEPS),
        is_complete=session.is_complete,
        assistant_response=last_message
    )


@app.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """Get the full conversation history of a session."""
    session = session_manager.get_session(session_id)
    
    history_items = [HistoryItem(**item) for item in session.history]
    
    return SessionHistoryResponse(
        session_id=session.session_id,
        history=history_items,
        is_complete=session.is_complete
    )


@app.delete("/sessions/{session_id}", response_model=SessionEndResponse)
async def end_session(session_id: str, save: bool = False):
    """End a session and optionally save the history."""
    session = session_manager.get_session(session_id)
    
    saved_path = None
    if save and session.history:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_path = f"reflection_session_{session_id[:8]}_{timestamp}.json"
        with open(saved_path, 'w', encoding='utf-8') as f:
            json.dump(session.history, f, ensure_ascii=False, indent=2)
    
    session_manager.delete_session(session_id)
    
    return SessionEndResponse(
        session_id=session_id,
        message="Session ended successfully",
        saved_path=saved_path
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_sessions": len(session_manager.sessions)
    }


if __name__ == "__main__":
    import uvicorn
    
    print("Starting Reflektor API server...")
    print("Make sure OPENAI_API_KEY is set in your environment.")
    print("API documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "navigate:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

