import os
from fastapi import FastAPI, Request

app = FastAPI()

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

state = {}

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/reset")
async def reset(request: Request):
    global state
    print("START reset")
    
    try:
        data = await request.json()
        print("STEP received input")
        
        state = {}
        
        print("END reset")
        return {"status": "success"}
    
    except Exception as e:
        print("ERROR:", str(e))
        return {"status": "error"}

@app.post("/step")
async def step(request: Request):
    print("START step")
    print("END step")
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/state")
def get_state():
    return state
