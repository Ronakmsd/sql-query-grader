---
title: SQL Query Grader
emoji: 🗄️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---
#SQL Query Grader — OpenEnv Environment

A real-world OpenEnv environment where an AI agent must write correct SQL queries
for business analytics tasks of increasing difficulty.

---

## Overview

This environment simulates a **business database analyst** scenario. The agent
receives a natural language task, a database schema, and must write the correct
SQL query. Feedback is provided after each attempt with partial scoring.

**Why SQL?** SQL is one of the most universally used real-world skills. Evaluating
LLM ability to write accurate SQL queries has direct practical value for
data teams, analytics platforms, and business intelligence tools.

---

## Database Schema

```
employees(id, name, department, salary, hire_date, manager_id)
departments(id, name, budget, location)
projects(id, name, department_id, start_date, end_date, status)
```

Sample: 10 employees, 4 departments, 5 projects (active/completed).

---

## Tasks

| Task | Difficulty | Description |
|------|-----------|-------------|
| easy | Easy | Filter employees by department, sort by salary |
| medium | Medium | GROUP BY with HAVING clause, aggregate functions |
| hard | Hard | Multi-table JOIN across employees, departments, projects |

---

## Reward Function

Each step returns a reward between 0.0 and 1.0:

- **Column correctness (30%)**: Are the correct columns returned?
- **Row count accuracy (30%)**: Is the number of rows correct?
- **Data accuracy (40%)**: Do the actual values match expected output?

Partial progress is rewarded — the agent gets credit for partially correct queries.

---

## Action & Observation Space

**Action:**
```json
{"query": "SELECT name, salary FROM employees WHERE department = 'Engineering'"}
```

**Observation:**
```json
{
  "task_description": "Find all employees in Engineering...",
  "schema_info": "employees(id, name, department, salary...)",
  "feedback": "Partially correct. Got 3 rows, expected 4.",
  "current_score": 0.6
}
```

---

## Setup & Run Locally

```bash
# Install dependencies
pip install openenv-core fastapi uvicorn openai pydantic

# Run server
cd server
uvicorn app:app --host 0.0.0.0 --port 8000

# Run inference
export HF_TOKEN=your_token_here
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
python inference.py
```

---

## Baseline Scores

| Task | Score |
|------|-------|
| easy | 0.95 |
| medium | 0.80 |
| hard | 0.65 |
| **Average** | **0.80** |

---

Built by **Ronak Bhanushali** for the Scaler x Meta PyTorch OpenEnv Hackathon 2026.
