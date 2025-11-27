# SwarajDesk RAG-Based Multilingual Chatbot Backend

A production-ready backend implementation of the SwarajDesk support chatbot powered by Retrieval-Augmented Generation (RAG). The system retrieves information from a structured knowledge base and generates accurate, context-aware responses without hallucination.

## Features

- **Retrieval-Augmented Generation**: Provides factual answers grounded in the knowledge base
- **Domain-Restricted Responses**: Strictly uses knowledge base only, preventing hallucinations
- **Multilingual Support**: Responds in English, Hindi, and Hinglish
- **Vector Search**: Efficient semantic search using ChromaDB
- **REST API**: Simple FastAPI endpoint for easy frontend integration
- **Persistent Storage**: Automatic embedding storage and reuse

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Framework | FastAPI |
| Vector Database | ChromaDB |
| Embedding Model | HuggingFace Sentence Transformer |
| LLM Provider | Groq |
| Data Format | JSON |

## Project Structure

```
project_root/
│
├── main.py                      # FastAPI backend with /chat endpoint
├── app.py                       # RAG pipeline: embeddings, retrieval, LLM
├── SwarajDesk_vectorDB.json     # Knowledge base dataset
├── chroma_store/                # Persistent ChromaDB storage (auto-created)
├── requirements.txt             # Project dependencies
├── .env                         # Environment variables (create this)
└── README.md                    # Documentation
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_key
HUGGINGFACEHUB_API_TOKEN=your_huggingface_key
LANGCHAIN_API_KEY=your_langchain_key  # optional
```

### 4. Start the Backend Server

```bash
uvicorn main:app --reload --port 8000
```

### 5. Test the API

Open the interactive API documentation:

```
http://127.0.0.1:8000/docs
```

## API Endpoint

### `POST /chat_swaraj`

Processes user queries and returns contextual responses from the knowledge base.

#### Request Body

```json
{
  "user_query": "<user message>",
  "language": "english" | "hindi" | "hinglish"
}
```

#### Example Request

```json
{
  "user_query": "How do I reset my password?",
  "language": "english"
}
```

#### Response Format

```json
{
  "bot_response": "<generated answer>"
}
```

#### Example Response

```json
{
  "bot_response": "To reset your password, go to the login page and click on 'Forgot Password'. You will receive a reset link via email."
}
```

## Dependencies

See `requirements.txt` for the complete list.

