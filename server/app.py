from fastapi import FastAPI
from models import SQLAction, SQLObservation
from server.my_env_environment import MyEnvEnvironment

app = FastAPI(
    title="SQL Query Grader",
    description="OpenEnv environment for SQL query evaluation",
    version="1.0.0"
)

envs = {
    "easy": MyEnvEnvironment("easy"),
    "medium": MyEnvEnvironment("medium"),
    "hard": MyEnvEnvironment("hard")
}

@app.get("/")
def root():
    return {
        "name": "sql-query-grader",
        "description": "SQL Query Grader - OpenEnv Environment",
        "tasks": ["easy", "medium", "hard"],
        "endpoints": ["/reset", "/step", "/state", "/health", "/docs"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(task: str = "easy"):
    return envs[task].reset()

@app.post("/step")
def step(action: dict, task: str = "easy"):
    return envs[task].step(action)

@app.get("/state")
def state(task: str = "easy"):
    return envs[task].state()
