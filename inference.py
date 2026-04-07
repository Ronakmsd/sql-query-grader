import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# ENV VARIABLES
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

# Dummy state
state_data = {}

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    global state_data
    state_data = {}
    return {"status": "success"}

@app.post("/step")
def step():
    return {"status": "step ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/state")
def state():
    return {"state": state_data}
