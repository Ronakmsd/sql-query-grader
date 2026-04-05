import sqlite3
from typing import Optional
from models import SQLAction, SQLObservation


def create_database():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary REAL, hire_date TEXT, manager_id INTEGER);
        CREATE TABLE departments (id INTEGER PRIMARY KEY, name TEXT, budget REAL, location TEXT);
        CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT, department_id INTEGER, start_date TEXT, end_date TEXT, status TEXT);
        INSERT INTO departments VALUES (1,'Engineering',500000,'Mumbai'),(2,'Marketing',200000,'Delhi'),(3,'Sales',300000,'Bangalore'),(4,'HR',150000,'Mumbai');
        INSERT INTO employees VALUES (1,'Rohan Sharma','Engineering',95000,'2020-01-15',NULL),(2,'Priya Patel','Engineering',85000,'2021-03-10',1),(3,'Amit Kumar','Marketing',70000,'2019-06-01',NULL),(4,'Sneha Joshi','Sales',60000,'2022-01-20',NULL),(5,'Raj Mehta','Engineering',90000,'2020-08-15',1),(6,'Pooja Singh','HR',55000,'2021-11-30',NULL),(7,'Vikram Das','Sales',65000,'2020-05-10',4),(8,'Neha Gupta','Marketing',72000,'2022-07-01',3),(9,'Arjun Nair','Engineering',88000,'2021-09-15',1),(10,'Kavya Reddy','HR',58000,'2023-02-01',6);
        INSERT INTO projects VALUES (1,'AI Platform',1,'2023-01-01','2023-12-31','completed'),(2,'Mobile App',1,'2023-06-01',NULL,'active'),(3,'Brand Campaign',2,'2023-03-01','2023-09-30','completed'),(4,'Sales CRM',3,'2023-07-01',NULL,'active'),(5,'HR Portal',4,'2023-08-01',NULL,'active');
    """)
    conn.commit()
    return conn


TASKS = {
    "easy": {
        "description": "Find all employees in Engineering. Return name and salary, ordered by salary descending.",
        "validation_query": "SELECT name, salary FROM employees WHERE department = 'Engineering' ORDER BY salary DESC",
        "expected_rows": 4,
        "hint": "Use SELECT, WHERE, ORDER BY on employees table."
    },
    "medium": {
        "description": "Find average salary per department. Return department and avg_salary only where avg > 70000, ordered by avg_salary descending.",
        "validation_query": "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department HAVING AVG(salary) > 70000 ORDER BY avg_salary DESC",
        "expected_rows": 2,
        "hint": "Use GROUP BY and HAVING."
    },
    "hard": {
        "description": "Find employees in departments with at least one active project. Return name, department, salary ordered by department then salary descending.",
        "validation_query": "SELECT e.name, e.department, e.salary FROM employees e JOIN departments d ON e.department = d.name JOIN projects p ON p.department_id = d.id WHERE p.status = 'active' GROUP BY e.id ORDER BY e.department, e.salary DESC",
        "expected_rows": 7,
        "hint": "Use JOIN across employees, departments, projects."
    }
}

SCHEMA_INFO = "Tables: employees(id,name,department,salary,hire_date,manager_id), departments(id,name,budget,location), projects(id,name,department_id,start_date,end_date,status)"


class MyEnvEnvironment:
    def _init_(self, task_name: str = "easy"):
        self.task_name = task_name
        self.task = TASKS[task_name]
        self.conn = create_database()
        self.attempts = 0
        self.best_score = 0.0
        self.last_feedback = "No query submitted yet."
        self.done = False

    def reset(self) -> dict:
        self.conn = create_database()
        self.attempts = 0
        self.best_score = 0.0
        self.done = False
        self.last_feedback = "Start writing your SQL query."
        return {
            "observation": {
                "task_description": self.task["description"],
                "schema_info": SCHEMA_INFO,
                "feedback": self.last_feedback,
                "current_score": 0.0
            },
            "reward": 0.0,
            "done": False,
            "info": {}
        }

    def step(self, action: dict) -> dict:
        self.attempts += 1
        score = 0.0
        query = action.get("query", "")
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            agent_results = cursor.fetchall()
            cursor.execute(self.task["validation_query"])
            expected_results = cursor.fetchall()
            col_score = 0.3 if cursor.description else 0.0
            if len(expected_results) > 0:
                row_score = 0.3 if len(agent_results) == len(expected_results) else 0.3 * min(len(agent_results), len(expected_results)) / max(len(agent_results), len(expected_results))
                matches = len(set(map(str, agent_results)) & set(map(str, expected_results)))
                data_score = 0.4 * matches / len(expected_results)
            else:
                row_score = 0.0
                data_score = 0.0
            score = round(col_score + row_score + data_score, 2)
            self.best_score = max(self.best_score, score)
            if score >= 0.95:
                feedback = f"Perfect! Score: {score}"
                self.done = True
            else:
                feedback = f"Got {len(agent_results)} rows, expected {len(expected_results)}. Score: {score}. Hint: {self.task['hint']}"
        except Exception as e:
            feedback = f"SQL Error: {str(e)}. Hint: {self.task['hint']}"
        if self.attempts >= 5:
            self.done = True
        self.last_feedback = feedback
        return {
            "observation": {
                "task_description": self.task["description"],
                "schema_info": SCHEMA_INFO,
                "feedback": feedback,
                "current_score": score
            },
            "reward": score,
            "done": self.done,
            "info": {"attempts": self.attempts, "best_score": self.best_score}
        }

    def state(self) -> dict:
        return {
            "task_description": self.task["description"],
            "schema_info": SCHEMA_INFO,
            "feedback": self.last_feedback,
            "current_score": self.best_score
        }
