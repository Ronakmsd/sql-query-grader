from pydantic import BaseModel
from typing import Optional


class SQLAction(BaseModel):
    """Action: the SQL query written by the agent"""
    query: str


class SQLObservation(BaseModel):
    """Observation returned after each step"""
    task_description: str
    schema_info: str
    feedback: str
    expected_output: Optional[str] = None
    current_score: float = 0.0


class SQLReward(BaseModel):
    """Reward signal"""
    value: float
    reason: str
