from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from loguru import logger
import uuid

from fastapi.security import OAuth2PasswordBearer

app = FastAPI(title="Groww Mutual Fund RAG API", version="1.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from qa_pipeline import QAPipeline

qa_pipeline = QAPipeline()
# -------------------------------

# --- Session Memory (In-Memory for now, use Redis in prod) ---
# Format: { "session_id": [{"role": "user", "text": "..."}, {"role": "assistant", "text": "..."}] }
sessions_db = {}
# -----------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    session_id: str = None

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    sources: list = []

def verify_token(token: str = Depends(oauth2_scheme)):
    # Dummy authentication logic
    if token != "supersecrettoken":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest, authenticated: bool = Depends(verify_token)):
    """
    Main endpoint for the chatbot. Orchestrates retrieval and LLM generation.
    """
    logger.info(f"Received query: {request.query}")
    
    session_id = request.session_id
    if not session_id or session_id not in sessions_db:
        if not session_id:
            session_id = str(uuid.uuid4())
        sessions_db[session_id] = []
        logger.info(f"Created/restored session: {session_id}")

    # Log user query to memory
    sessions_db[session_id].append({"role": "user", "text": request.query})
    
    # 1. Check Cache (e.g., Redis) for exact query match to save LLM cost
    # (Implementation omitted for brevity)

    # 2. RAG Pipeline execution
    try:
        response = qa_pipeline.ask(request.query)
        answer = response["result"]
        
        # Log assistant response to memory
        sessions_db[session_id].append({"role": "assistant", "text": answer})
        
        # 3. Analytics & Monitoring logging
        logger.info(f"Successfully answered query for session {session_id}")
        
        return QueryResponse(answer=answer, session_id=session_id, sources=[])
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during RAG generation")

@app.get("/health")
def health_check():
    return {"status": "healthy", "components": ["api", "vector_db", "llm"]}

