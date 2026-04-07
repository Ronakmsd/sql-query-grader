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

    print("START")
    try:
        _ = await request.json()   # important: request read
        
        state = {}

        print("STEP")
        print("END")

        return {"success": True}
    
    except Exception as e:
        print("ERROR", str(e))
        return {"success": False}

@app.post("/step")
async def step(request: Request):
    print("START")
    print("END")
    return {"success": True}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/state")
def get_state():
    return state
