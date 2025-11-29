## importing necessary tokens and environement keys
import os
from dotenv import load_dotenv
load_dotenv()
import json

## importing necessay modules and library to build gen AI application
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser   
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
from chromadb import PersistentClient
import streamlit as st
import warnings
warnings.filterwarnings('ignore')


## Groq api key and setting hugging face environment
Groq_api_key = os.getenv('GROQ_API_KEY')
client = os.getenv("HUGGINGFACEHUB_API_TOKEN")

## Langsmith tracking
os.environ["LANGCHAIN_API_KEY"]= os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]= "true"
os.environ["LANGCHAIN_PROJECT"]= "Swaraj Desk interactive multi-lingual RAG chatbot"

## Importing the JSON data
with open("SwarajDesk_vectorDB.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# print(len(data)) #original JSON length


## Vector embeddings using Hugging face sentence transformer
embeddings_list = []   # to store all embeddings + metadata

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

for record in data:
    content = record["content"]
    embedding = embedding_model.embed_query(content)
    
    embeddings_list.append({
        "embedding": embedding,
        "title": record["title"],
        "content": record["content"],
        "tags": record["tags"]
    })

# print(len(embeddings_list))  # should match original JSON length 


## storing embedding vectors in chromaDB

# initialize chroma client
client = PersistentClient(path="./chroma_store")


# create / load collection
collection = client.get_or_create_collection(
    name="swarajdesk_chroma_db",       # changed for better naming
    metadata={"hnsw:space": "cosine"}   # similarity metric
)

# store embeddings + metadata in chroma
for idx, item in enumerate(embeddings_list):
    collection.add(
    ids=[str(idx)],
    embeddings=[item["embedding"]],
    documents=[item["content"]],
    metadatas=[
        {
            "title": item["title"],
            "content": item["content"],
            "tags": ", ".join(item["tags"])    # FIX: convert list → string
        }
    ]
)

print("Embeddings stored successfully in ChromaDB!")
# number of stored records.
print(collection.count())                     



## Function to retrieve context from ChromaDB based on user query

def retrieve_context(user_query: str, collection, k: int = 5):
    # 1) Embed the user query using HuggingFace embeddings model
    query_embedding = embedding_model.embed_query(user_query)

    # 2) Query ChromaDB for similarity
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    metadatas = results["metadatas"][0]
    documents = results.get("documents", [[]])[0]

    return metadatas, documents


## checking the user query and embedding vector from chromaDB

# test_query = "How can I reset my password?"
# metadatas, docs = retrieve_context(test_query, collection, k=5)

# print("\nRetrieved Chunks for Query:", test_query)
# for idx, m in enumerate(metadatas):
#     print(f"\nResult #{idx + 1}")
#     print("Title:", m["title"])
#     print("Tags:", m["tags"])
#     print("Content Preview:", m["content"][:200], "...")


# context-building

def build_context_text(metadatas):
    context_parts = []
    for i, m in enumerate(metadatas):
        title = m.get("title", f"Chunk {i+1}")
        content = m.get("content", "")
        context_parts.append(f"[{i+1}] {title}\n{content}")
    
    context_text = "\n\n---\n\n".join(context_parts)
    return context_text


# Checking the context text before sending to the LLM

# query = "How can I reset my password?"
# metadatas, docs = retrieve_context(query, collection, k=5)

# context_text = build_context_text(metadatas)

# print("\nGENERATED CONTEXT:\n")
# print(context_text)


SYSTEM_PROMPT = """
You are a strict, kind and helpful support assistant for Swaraj Desk.
When replying, strictly use ONLY the language specified by the user:
- english = response fully in English
- hindi = response fully in pure Hindi (Devanagari)
- hinglish = response in Hindi but written in English alphabets
  Never mix languages.

RULES:
- Answer ONLY using the information provided in the context.
- If the answer is not clearly present in the context, say:
  "I can only assist with information related to Swaraj Desk and the data I have been given."
- Do NOT invent new policies, rules, or features.
- If the user asks about topics unrelated to the portal (personal life, politics, exams, etc.), reply with the same message above.
- Be concise, clear, and polite.
"""


def answer_user_query(user_query: str, collection, language: str = "english"):
    # 1) Retrieve context
    metadatas, _ = retrieve_context(user_query, collection, k=5)
    context_text = build_context_text(metadatas)

    # 2) Language instruction
    if language.lower() == "hindi":
        language_instruction = "Your response must be fully in Hindi. Do not use English words unless they are technical terms."
    elif language.lower() == "hinglish":
        language_instruction = "Your response must be in Hinglish: use Hindi language but written in English alphabets. Do not use Devanagari script. For example: 'aap login page par click karein'."
    else:
        language_instruction = "Your response must be fully in English."

    # 3) Prompt with strict context usage
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"{language_instruction}\n\n"
                f"User question:\n{user_query}\n\n"
                f"Use ONLY the following context to answer:\n\n{context_text}"
            )
        }
    ]

    # 4) Call Groq model 
    model = ChatGroq(model="openai/gpt-oss-120b", groq_api_key=Groq_api_key)
    response = model.invoke(messages)

    return response.content


## TESTING 

# Interact in English with user

# reply = answer_user_query(
#     "How can I reset my password?",
#     collection,
#     language="english"
# )
# print(reply)


# Interact in hindi with user

# reply = answer_user_query(
#     "Password reset karne ka tarika kya hai?",
#     collection,
#     language="hindi"
# )
# print(reply)

# reply = answer_user_query(
#     "Password reset karne ka tarika kya hai?",
#     collection,
#     language="hinglish"
# )
# print(reply)


## FINAL TESTING
user_question = "How can I reset my password?"
reply = answer_user_query(user_question, collection)

print("User:", user_question)
print("Bot :", reply)






