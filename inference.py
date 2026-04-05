"""
SQL Query Grader - Baseline Inference Script
============================================
Runs an LLM agent against all 3 SQL tasks (easy, medium, hard).
Follows the required [START] [STEP] [END] stdout format.
"""

import asyncio
import os
from typing import List, Optional
from openai import OpenAI
from my_env_environment import MyEnvEnvironment
from models import SQLAction

# ─── Config ────────────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")

MAX_STEPS = 5
TEMPERATURE = 0.2
MAX_TOKENS = 300
SUCCESS_SCORE_THRESHOLD = 0.8

SYSTEM_PROMPT = """You are an expert SQL developer. 
You will be given a database schema and a task. 
Write a single, correct SQL SELECT query to solve the task.
Reply with ONLY the SQL query — no explanation, no markdown, no backticks.
Just raw SQL starting with SELECT."""


# ─── Logging (required format) ─────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


# ─── LLM Call ──────────────────────────────────────────────────────────────────

def get_sql_from_llm(client: OpenAI, task_desc: str, schema: str, feedback: str, history: List[str]) -> str:
    history_block = "\n".join(history[-3:]) if history else "None"

    user_prompt = f"""Database Schema:
{schema}

Task:
{task_desc}

Previous feedback:
{feedback}

Previous attempts:
{history_block}

Write the correct SQL query now:"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        query = (completion.choices[0].message.content or "").strip()
        # Clean up if model adds backticks
        query = query.replace("```sql", "").replace("```", "").strip()
        return query
    except Exception as exc:
        print(f"[DEBUG] LLM call failed: {exc}", flush=True)
        return "SELECT 1"


# ─── Run one task ──────────────────────────────────────────────────────────────

async def run_task(client: OpenAI, task_name: str) -> float:
    env_name = "sql-query-grader"
    log_start(task=task_name, env=env_name, model=MODEL_NAME)

    env = MyEnvEnvironment(task_name=task_name)
    obs = env.reset()

    rewards: List[float] = []
    history: List[str] = []
    steps_taken = 0
    score = 0.0
    success = False
    error = None

    try:
        for step in range(1, MAX_STEPS + 1):
            if obs.feedback and "done" in obs.feedback.lower():
                break

            # Get SQL from LLM
            query = get_sql_from_llm(
                client,
                obs.task_description,
                obs.schema_info,
                obs.feedback,
                history,
            )

            action = SQLAction(query=query)

            try:
                result = env.step(action)
                obs = result.observation
                reward = result.reward or 0.0
                done = result.done
                error = None
            except Exception as e:
                reward = 0.0
                done = False
                error = str(e)

            rewards.append(reward)
            steps_taken = step
            history.append(f"Step {step}: {query} → reward {reward:.2f}")

            log_step(step=step, action=query[:80], reward=reward, done=done, error=error)

            if done:
                break

        score = max(rewards) if rewards else 0.0
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


# ─── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    tasks = ["easy", "medium", "hard"]
    all_scores = []

    for task_name in tasks:
        score = await run_task(client, task_name)
        all_scores.append(score)
        print(f"[DEBUG] Task '{task_name}' completed with score: {score:.3f}", flush=True)

    avg_score = sum(all_scores) / len(all_scores)
    print(f"[DEBUG] Average score across all tasks: {avg_score:.3f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
