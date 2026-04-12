import os
import re
import json
import sqlite3
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sql_grader_server")

app = FastAPI(title="SQL Query Grader Server", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[""], allow_methods=[""], allow_headers=["*"])

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    budget REAL NOT NULL,
    location TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    salary REAL NOT NULL,
    hire_date TEXT NOT NULL,
    role TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    budget REAL NOT NULL,
    start_date TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
CREATE TABLE IF NOT EXISTS employee_projects (
    employee_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    hours_allocated INTEGER NOT NULL,
    PRIMARY KEY (employee_id, project_id),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
"""

SEED_DATA_SQL = """
INSERT OR IGNORE INTO departments VALUES
(1,'Engineering',1500000,'Mumbai'),
(2,'Marketing',800000,'Delhi'),
(3,'Finance',1000000,'Bangalore'),
(4,'HR',500000,'Pune'),
(5,'Research',2000000,'Hyderabad');

INSERT OR IGNORE INTO employees VALUES
(1,'Rohan Mehta',1,95000,'2020-01-15','Senior Engineer'),
(2,'Priya Sharma',1,88000,'2021-03-10','Engineer'),
(3,'Amit Kumar',2,72000,'2019-07-22','Marketing Lead'),
(4,'Sneha Patel',3,110000,'2018-11-05','Finance Manager'),
(5,'Vikram Singh',1,65000,'2022-06-18','Junior Engineer'),
(6,'Anita Desai',4,58000,'2020-09-30','HR Specialist'),
(7,'Rajesh Nair',5,125000,'2017-04-12','Research Lead'),
(8,'Meera Joshi',2,68000,'2021-12-01','Marketing Analyst'),
(9,'Karan Malhotra',1,92000,'2019-08-14','Senior Engineer'),
(10,'Deepa Reddy',3,79000,'2022-02-28','Analyst');

INSERT OR IGNORE INTO projects VALUES
(1,'AI Platform',1,'active',500000,'2024-01-01'),
(2,'Brand Refresh',2,'active',200000,'2024-03-01'),
(3,'Cost Analysis',3,'completed',150000,'2023-06-01'),
(4,'Talent Pipeline',4,'active',100000,'2024-02-01'),
(5,'ML Research',5,'active',800000,'2023-09-01'),
(6,'DevOps Upgrade',1,'active',300000,'2024-04-01'),
(7,'Market Expansion',2,'inactive',400000,'2023-01-01');

INSERT OR IGNORE INTO employee_projects VALUES
(1,1,40),(2,1,30),(9,1,35),
(3,2,40),(8,2,25),
(4,3,20),(10,3,30),
(6,4,40),(7,5,40),
(1,6,20),(5,6,40);
"""

TASKS = {
    "easy": {
        "description": "Find all Engineering department employees earning above 80000, sorted by salary descending.",
        "schema_info": "employees(id,name,department_id,salary,hire_date,role), departments(id,name,budget,location)",
        "expected_sql": "SELECT e.name, e.salary, e.role FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.name = 'Engineering' AND e.salary > 80000 ORDER BY e.salary DESC",
        "difficulty": "easy", "max_steps": 5
    },
    "medium": {
        "description": "For each department, calculate average salary and headcount. Only show departments with average salary above 70000, ordered by average salary descending.",
        "schema_info": "employees(id,name,department_id,salary,hire_date,role), departments(id,name,budget,location)",
        "expected_sql": "SELECT d.name, AVG(e.salary) as avg_salary, COUNT(e.id) as headcount FROM departments d JOIN employees e ON d.id = e.department_id GROUP BY d.id, d.name HAVING AVG(e.salary) > 70000 ORDER BY avg_salary DESC",
        "difficulty": "medium", "max_steps": 5
    },
    "hard": {
        "description": "Find employees on active projects in Engineering or Research departments, with project names and hours. Sort by hours_allocated descending.",
        "schema_info": "employees(id,name,department_id,salary,hire_date,role), departments(id,name,budget,location), projects(id,name,department_id,status,budget,start_date), employee_projects(employee_id,project_id,hours_allocated)",
        "expected_sql": "SELECT e.name, d.name as department, p.name as project, ep.hours_allocated FROM employees e JOIN departments d ON e.department_id = d.id JOIN employee_projects ep ON e.id = ep.employee_id JOIN projects p ON ep.project_id = p.id WHERE p.status = 'active' AND d.name IN ('Engineering','Research') ORDER BY ep.hours_allocated DESC",
        "difficulty": "hard", "max_steps": 5
    }
}

session_state = {"current_task": None, "step_count": 0, "done": False, "history": []}


def get_db():
    conn = sqlite3.connect("/tmp/sql_grader.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_DATA_SQL)
    conn.commit()
    conn.close()


def execute_sql(query: str):
    try:
        conn = get_db()
        cursor = conn.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"success": True, "rows": rows, "count": len(rows)}
    except Exception as e:
        return {"success": False, "error": str(e), "rows": [], "count": 0}


def compute_score(expected_sql: str, submitted_sql: str) -> float:
    exp = execute_sql(expected_sql)
    sub = execute_sql(submitted_sql)
    if not sub["success"]:
        return 0.05
    exp_rows = exp.get("rows", [])
    sub_rows = sub.get("rows", [])
    if not exp_rows and not sub_rows:
        return 0.5
    exp_cols = set(exp_rows[0].keys()) if exp_rows else set()
    sub_cols = set(sub_rows[0].keys()) if sub_rows else set()
    col_score = len(exp_cols & sub_cols) / max(len(exp_cols), 1) * 0.30
    row_ratio = min(len(sub_rows), len(exp_rows)) / max(len(exp_rows), 1) if exp_rows else 0.5
    row_score = row_ratio * 0.30
    exp_set = set(json.dumps(sorted(r.items())) for r in exp_rows)
    sub_set = set(json.dumps(sorted(r.items())) for r in sub_rows)
    data_score = (len(exp_set & sub_set) / max(len(exp_set), 1)) * 0.40
    raw = col_score + row_score + data_score
    if raw <= 0.0:
        return 0.05
    if raw >= 1.0:
        return 0.95
    return round(raw, 4)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "service": "SQL Query Grader v2.0", "tasks": list(TASKS.keys())}


@app.get("/health")
def health():
    return {"status": "healthy", "tasks": list(TASKS.keys())}


@app.post("/reset")
def reset(body: dict = {}):
    task_name = (body or {}).get("task", "easy")
    if task_name not in TASKS:
        task_name = "easy"
    task = TASKS[task_name]
    session_state.update({"current_task": task_name, "step_count": 0, "done": False, "history": []})
    return {
        "status": "reset",
        "observation": {
            "task_description": task["description"],
            "schema_info": task["schema_info"],
            "difficulty": task["difficulty"],
            "feedback": "Submit your SQL query via /step",
            "current_score": None,
            "ready": True
        },
        "done": False,
        "reward": None
    }


@app.post("/step")
def step(body: dict):
    task_name = session_state.get("current_task", "easy")
    if task_name not in TASKS:
        raise HTTPException(status_code=400, detail="Call /reset first")
    task = TASKS[task_name]
    submitted_sql = body.get("query", body.get("action", ""))
    if not submitted_sql:
        return {"observation": {"success": False, "feedback": "No SQL provided", "current_score": 0.05}, "reward": 0.05, "done": False}
    exec_result = execute_sql(submitted_sql)
    score = compute_score(task["expected_sql"], submitted_sql)
    session_state["step_count"] += 1
    session_state["history"].append({"step": session_state["step_count"], "score": score})
    done = score >= 0.85 or session_state["step_count"] >= task["max_steps"]
    session_state["done"] = done
    if not exec_result["success"]:
        feedback = "SQL Error: " + exec_result.get("error", "")
    elif score >= 0.85:
        feedback = "Excellent! Query is correct."
    elif score >= 0.6:
        feedback = "Partially correct. Check columns and conditions."
    else:
        feedback = "Incorrect. Review JOIN and WHERE clauses."
    return {
        "observation": {
            "success": exec_result["success"],
            "tool_result": exec_result.get("rows", [])[:5],
            "feedback": feedback,
            "current_score": score
        },
        "reward": score,
        "done": done
    }


@app.get("/state")
def state(verify_queries: list[str] = []):
    results = [execute_sql(q) for q in verify_queries]
    return {"current_task": session_state.get("current_task"), "step_count": session_state.get("step_count"), "done": session_state.get("done"), "history": session_state.get("history", []), "verification_results": results}


@app.post("/grade")
def grade(body: dict):
    expected = body.get("expected_query", "")
    submitted = body.get("submitted_query", "")
    if not expected or not submitted:
        raise HTTPException(status_code=400, detail="Both queries required")
    score = compute_score(expected, submitted)
    return {"score": score, "success": True}


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()
