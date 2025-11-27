# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app import answer_user_query

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
def chat(req: ChatRequest):
    answer = answer_user_query(req.user_query, req.language)
    return ChatResponse(bot_response=answer)
