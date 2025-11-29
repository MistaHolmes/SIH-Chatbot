# main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app import answer_user_query, collection

app = FastAPI(title="Swaraj_chat Backend API")

# ----- allow frontend access -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can change to your website domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- request model -----
class ChatRequest(BaseModel):
    user_query: str
    language: str = "english"

# ----- response model -----
class ChatResponse(BaseModel):
    bot_response: str

# ----- /chat endpoint -----
@app.post("/chat_swaraj", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    """Accepts a JSON body with `user_query` and optional `language`.

    Enforces `Content-Type: application/json` and returns 415 if not provided.
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        raise HTTPException(status_code=415, detail="Content-Type must be application/json")

    # pass the chroma collection from app to the answer function
    answer = answer_user_query(req.user_query, collection, req.language)
    return ChatResponse(bot_response=answer)


# Simple health-check endpoint
@app.get("/health")
def health():
    """Basic health endpoint to verify the server is running."""
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "THis is the SwarjDesk RAG-Based Multilingual Chatbot Backend"}