"""
Vercel serverless function for /api/sessions endpoint
"""
import os
import uuid
import json
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

# Load environment variables
load_dotenv(override=True)

# Constants
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
DEFAULT_TEMPERATURE = 0.4
DEFAULT_MAX_TOKENS = 500

# System prompt and steps
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

# Pydantic models
class SessionCreateResponse(BaseModel):
    session_id: str
    message: str
    current_step: int
    step_title: str
    step_question: str

class SessionResponse(BaseModel):
    session_id: str
    current_step: int
    step_title: str
    step_question: str
    is_complete: bool
    created_at: str

class UserInput(BaseModel):
    user_input: str

class AssistantResponse(BaseModel):
    session_id: str
    assistant_response: str
    current_step: int
    step_title: str
    is_complete: bool
    should_advance: bool

class SessionEndResponse(BaseModel):
    session_id: str
    message: str
    saved_path: Optional[str] = None

# Session management (in-memory for serverless)
class ReflectionSession:
    def __init__(self, session_id: str, chain, message_history, current_step_index: int = 0):
        self.session_id = session_id
        self.chain = chain
        self.message_history = message_history
        self.current_step_index = current_step_index
        self.history = []
        self.is_complete = False
        self.created_at = datetime.datetime.now()

# Global session storage (for serverless, consider using a database in production)
sessions: Dict[str, ReflectionSession] = {}

def create_session():
    """Create a new reflection session."""
    session_id = str(uuid.uuid4())

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is missing. Add it to Vercel environment variables."
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
        current_step_index=0
    )
    
    sessions[session_id] = session
    return session

def get_session(session_id: str):
    """Get an existing session or raise error."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

# Vercel serverless function handler
def handler(request):
    """Main handler for Vercel serverless function."""
    try:
        # Parse request
        if request.method == "POST" and request.path == "/api/sessions":
            # Create new session
            session = create_session()
            current_step = STEPS[session.current_step_index]
            
            # Add initial message to history
            session.message_history.add_user_message("Start the reflection exercise.")
            
            # Get initial response from AI
            response = session.chain.invoke({
                "history": session.message_history.messages,
                "input": current_step["question"]
            })
            
            session.message_history.add_ai_message(response.content)
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                "body": json.dumps({
                    "session_id": session.session_id,
                    "message": "Session created successfully",
                    "current_step": current_step["id"],
                    "step_title": current_step["title"],
                    "step_question": current_step["question"]
                })
            }
        
        elif request.method == "POST" and "/api/sessions/" in request.path and "/respond" in request.path:
            # Submit user response
            import re
            session_id_match = re.search(r'/api/sessions/([^/]+)/respond', request.path)
            if not session_id_match:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Invalid session ID"})
                }
            
            session_id = session_id_match.group(1)
            session = get_session(session_id)
            
            # Parse user input
            try:
                body = json.loads(request.body)
                user_input = body.get("user_input", "")
            except:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Invalid JSON body"})
                }
            
            # Add user input to history
            session.message_history.add_user_message(user_input)
            session.history.append({
                "step": STEPS[session.current_step_index]["id"],
                "title": STEPS[session.current_step_index]["title"],
                "user_input": user_input,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Get AI response
            current_step = STEPS[session.current_step_index]
            response = session.chain.invoke({
                "history": session.message_history.messages,
                "input": f"User responded to '{current_step['title']}': {user_input}"
            })
            
            assistant_response = response.content
            session.message_history.add_ai_message(assistant_response)
            
            # Check if should advance
            should_advance = "[ADVANCE]" in assistant_response
            if should_advance:
                session.current_step_index += 1
                if session.current_step_index >= len(STEPS):
                    session.is_complete = True
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                "body": json.dumps({
                    "session_id": session.session_id,
                    "assistant_response": assistant_response.replace("[ADVANCE]", "").strip(),
                    "current_step": session.current_step_index + 1 if session.current_step_index < len(STEPS) else len(STEPS),
                    "step_title": STEPS[session.current_step_index]["title"] if session.current_step_index < len(STEPS) else "Complete",
                    "is_complete": session.is_complete,
                    "should_advance": should_advance
                })
            }
        
        elif request.method == "GET" and "/api/sessions/" in request.path and "/history" not in request.path:
            # Get session state
            import re
            session_id_match = re.search(r'/api/sessions/([^/]+)', request.path)
            if not session_id_match:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Invalid session ID"})
                }
            
            session_id = session_id_match.group(1)
            session = get_session(session_id)
            current_step = STEPS[session.current_step_index] if session.current_step_index < len(STEPS) else None
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                "body": json.dumps({
                    "session_id": session.session_id,
                    "current_step": current_step["id"] if current_step else len(STEPS),
                    "step_title": current_step["title"] if current_step else "Complete",
                    "step_question": current_step["question"] if current_step else "",
                    "is_complete": session.is_complete,
                    "created_at": session.created_at.isoformat()
                })
            }
        
        elif request.method == "GET" and "/api/sessions/" in request.path and "/history" in request.path:
            # Get session history
            import re
            session_id_match = re.search(r'/api/sessions/([^/]+)/history', request.path)
            if not session_id_match:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Invalid session ID"})
                }
            
            session_id = session_id_match.group(1)
            session = get_session(session_id)
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                "body": json.dumps({
                    "session_id": session.session_id,
                    "history": session.history,
                    "created_at": session.created_at.isoformat()
                })
            }
        
        elif request.method == "DELETE" and "/api/sessions/" in request.path:
            # End session
            import re
            session_id_match = re.search(r'/api/sessions/([^/]+)', request.path)
            if not session_id_match:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Invalid session ID"})
                }
            
            session_id = session_id_match.group(1)
            session = get_session(session_id)
            
            # Parse save parameter
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(request.url)
            save = parse_qs(parsed_url.query).get('save', ['false'])[0].lower() == 'true'
            
            saved_path = None
            if save and session.history:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                saved_path = f"reflection_session_{session_id[:8]}_{timestamp}.json"
                # In serverless, you might want to save to a database or cloud storage
            
            # Delete session
            if session_id in sessions:
                del sessions[session_id]
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                "body": json.dumps({
                    "session_id": session_id,
                    "message":Session ended successfully",
                    "saved_path": saved_path
                })
            }
        
        elif request.method == "GET" and request.path == "/api/health":
            # Health check
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                "body": json.dumps({
                    "status": "healthy",
                    "active_sessions": len(sessions)
                })
            }
        
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"detail": "Endpoint not found"})
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"detail": str(e)})
        }

# Export for Vercel
app = handler
