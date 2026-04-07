from fastapi import FastAPI, Request

app = FastAPI()

state = {}

@app.post("/reset")
async def reset(request: Request):
    global state
    print("START")
    state = {}
    print("STEP")
    print("END")
    return {"success": True}

@app.post("/step")
async def step(request: Request):
    print("START")
    print("END")
    return {"success": True}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/state")
def state_api():
    return state
