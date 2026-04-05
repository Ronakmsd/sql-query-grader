from fastapi import FastAPI
from models import SQLAction, SQLObservation
from server.my_env_environment import MyEnvEnvironment

app = FastAPI()
env = MyEnvEnvironment()

@app.post("/reset")
def reset():
    return env.reset()

@app.post("/step")
def step(action: dict):
    return env.step(action)

@app.get("/state")
def state():
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}
