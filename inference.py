import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# ENV VARIABLES
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

# REQUEST FORMAT
class QueryRequest(BaseModel):
    query: str

# REQUIRED ENDPOINTS

@app.get("/")
def home():
    return {"message": "SQL Query Grader running"}

@app.post("/reset")
def reset():
    return {"status": "reset done"}

@app.post("/step")
def step():
    return {"status": "step ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/state")
def state():
    return {"state": "ok"}

@app.get("/docs")
def docs():
    return {"docs": "available"}
