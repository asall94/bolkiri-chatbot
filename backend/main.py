from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime
from dotenv import load_dotenv
from ai_agent import AIAgent

load_dotenv()

app = FastAPI(title="Bolkiri Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = None

@app.on_event("startup")
async def startup_event():
    global agent
    api_key = os.getenv("OPENAI_API_KEY")
    website_url = os.getenv("WEBSITE_URL", "https://bolkiri.fr")
    
    if not api_key:
        print("WARNING: OPENAI_API_KEY not set")
        return
    
    print(f"Initializing agent...")
    
    try:
        agent = AIAgent(openai_api_key=api_key, website_url=website_url)
        # KB enrichie déjà chargée dans __init__, pas besoin de scraper
        print(f"Agent initialized successfully with {len(agent.kb.get_all_restaurants())} restaurants")
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        import traceback
        traceback.print_exc()

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.get("/")
@app.head("/")
@app.options("/")
async def read_root():
    """Root endpoint - serves index.html or returns status for HEAD/OPTIONS requests"""
    return {"status": "ok", "service": "Bolkiri Chatbot API", "version": "1.0.1"}

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    global agent
    
    if agent is None:
        raise HTTPException(status_code=503, detail="AI Agent not initialized")
    
    try:
        conversation_id = chat_message.conversation_id or f"conv_{datetime.now().timestamp()}"
        
        response_text = agent.chat(chat_message.message, conversation_id)
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh-knowledge")
async def refresh_knowledge(background_tasks: BackgroundTasks):
    """Endpoint pour rafraîchir la KB manuellement"""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Lancer le refresh en arrière-plan
    background_tasks.add_task(agent.refresh_knowledge_from_web)
    
    return {
        "status": "refresh_started",
        "restaurants": len(agent.kb.get_all_restaurants()),
        "last_update": agent.agent_state.get('last_update', 'never')
    }

@app.get("/health")
@app.head("/health")
@app.options("/health")
async def health_check():
    """Health check endpoint for monitoring services like Render (supports GET/HEAD/OPTIONS)"""
    return {
        "status": "healthy",
        "agent_ready": agent is not None,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
