from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime
from dotenv import load_dotenv
from ai_agent import AIAgent
from logger_config import setup_logger

load_dotenv()

# Setup structured JSON logging
logger = setup_logger(__name__)

app = FastAPI(title="Bolkiri Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

agent = None

@app.on_event("startup")
async def startup_event():
    global agent
    api_key = os.getenv("OPENAI_API_KEY")
    website_url = os.getenv("WEBSITE_URL", "https://bolkiri.fr")
    
    if not api_key:
        logger.warning("OPENAI_API_KEY not set - agent initialization skipped")
        return
    
    logger.info("Initializing AI agent...")
    
    try:
        agent = AIAgent(openai_api_key=api_key, website_url=website_url)
        # Enriched KB already loaded in __init__, no need to scrape
        restaurant_count = len(agent.kb.get_all_restaurants())
        logger.info("Agent initialized successfully", extra={"restaurant_count": restaurant_count})
    except Exception as e:
        logger.error("Failed to initialize agent", extra={"error_type": type(e).__name__, "error_message": str(e)}, exc_info=True)

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Root endpoint - serves the chat interface"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return {"status": "ok", "service": "Bolkiri Chatbot API", "version": "1.0.2"}

@app.head("/")
@app.options("/")
async def root_options():
    """HEAD and OPTIONS for monitoring"""
    return {"status": "ok"}

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
    
    # Launch refresh in background
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
