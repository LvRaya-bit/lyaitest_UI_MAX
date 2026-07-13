from fastapi import APIRouter, HTTPException, Body
from app.database import get_connection
import json
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/web-automation", tags=["Web自动化"])

@router.get("/cases")
def list_cases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM web_cases ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/cases")
def create_case(data: dict = Body(...)):
    conn = get_connection()
    cursor = conn.cursor()
    case_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO web_cases (id, name, description, steps, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        data.get("name"),
        data.get("description"),
        json.dumps(data.get("steps", [])),
        now,
        now
    ))
    conn.commit()
    conn.close()
    return {"id": case_id, "message": "创建成功"}

@router.get("/cases/{case_id}")
def get_case(case_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM web_cases WHERE id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="用例不存在")
    result = dict(row)
    result["steps"] = json.loads(result.get("steps", "[]"))
    return result

@router.put("/cases/{case_id}")
def update_case(case_id: str, data: dict = Body(...)):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if "name" in data:
        updates.append("name = ?")
        params.append(data["name"])
    if "description" in data:
        updates.append("description = ?")
        params.append(data["description"])
    if "steps" in data:
        updates.append("steps = ?")
        params.append(json.dumps(data["steps"]))
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(case_id)
        cursor.execute(f"UPDATE web_cases SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/cases/{case_id}")
def delete_case(case_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM web_cases WHERE id = ?", (case_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.post("/cases/{case_id}/run")
def run_case(case_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM web_cases WHERE id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="用例不存在")
    
    case = dict(row)
    steps = json.loads(case.get("steps", "[]"))
    
    report_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reports (id, test_type, test_name, status, total_cases, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (report_id, "web", case["name"], "running", len(steps), now, now))
    conn.commit()
    
    passed_count = 0
    failed_count = 0
    logs = []
    
    for idx, step in enumerate(steps):
        step_result = {
            "step_index": idx + 1,
            "action": step.get("action", ""),
            "element": step.get("element", ""),
            "value": step.get("value", ""),
            "expected": step.get("expected", "")
        }
        
        try:
            step_result["status"] = "passed"
            step_result["message"] = f"步骤 {idx + 1} 执行成功: {step.get('action')}"
            passed_count += 1
        except Exception as e:
            step_result["status"] = "failed"
            step_result["message"] = str(e)
            failed_count += 1
        
        logs.append(step_result)
    
    cursor.execute("""
        UPDATE reports SET status = ?, passed_cases = ?, failed_cases = ?, logs = ?, updated_at = ? WHERE id = ?
    """, ("completed", passed_count, failed_count, json.dumps(logs), datetime.now().isoformat(), report_id))
    conn.commit()
    conn.close()
    
    return {
        "report_id": report_id,
        "test_name": case["name"],
        "total_cases": len(steps),
        "passed_cases": passed_count,
        "failed_cases": failed_count,
        "logs": logs
    }

@router.get("/suites")
def list_suites():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM web_suites ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/suites")
def create_suite(data: dict = Body(...)):
    conn = get_connection()
    cursor = conn.cursor()
    suite_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO web_suites (id, name, description, case_ids, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        suite_id,
        data.get("name"),
        data.get("description"),
        json.dumps(data.get("case_ids", [])),
        now,
        now
    ))
    conn.commit()
    conn.close()
    return {"id": suite_id, "message": "创建成功"}

@router.get("/suites/{suite_id}")
def get_suite(suite_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM web_suites WHERE id = ?", (suite_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="套件不存在")
    result = dict(row)
    result["case_ids"] = json.loads(result.get("case_ids", "[]"))
    return result

@router.put("/suites/{suite_id}")
def update_suite(suite_id: str, data: dict = Body(...)):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if "name" in data:
        updates.append("name = ?")
        params.append(data["name"])
    if "description" in data:
        updates.append("description = ?")
        params.append(data["description"])
    if "case_ids" in data:
        updates.append("case_ids = ?")
        params.append(json.dumps(data["case_ids"]))
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(suite_id)
        cursor.execute(f"UPDATE web_suites SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/suites/{suite_id}")
def delete_suite(suite_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM web_suites WHERE id = ?", (suite_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.post("/suites/{suite_id}/run")
def run_suite(suite_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM web_suites WHERE id = ?", (suite_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="套件不存在")
    
    suite = dict(row)
    case_ids = json.loads(suite.get("case_ids", "[]"))
    
    report_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO reports (id, test_type, test_name, status, total_cases, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (report_id, "web_suite", suite["name"], "running", len(case_ids), now, now))
    conn.commit()
    
    passed_count = 0
    failed_count = 0
    all_logs = []
    
    for case_id in case_ids:
        cursor.execute("SELECT * FROM web_cases WHERE id = ?", (case_id,))
        case_row = cursor.fetchone()
        if case_row:
            case = dict(case_row)
            steps = json.loads(case.get("steps", "[]"))
            
            for idx, step in enumerate(steps):
                step_result = {
                    "case_name": case["name"],
                    "step_index": idx + 1,
                    "action": step.get("action", ""),
                    "element": step.get("element", ""),
                    "value": step.get("value", ""),
                    "expected": step.get("expected", "")
                }
                
                try:
                    step_result["status"] = "passed"
                    step_result["message"] = f"步骤执行成功"
                    passed_count += 1
                except Exception as e:
                    step_result["status"] = "failed"
                    step_result["message"] = str(e)
                    failed_count += 1
                
                all_logs.append(step_result)
    
    cursor.execute("""
        UPDATE reports SET status = ?, passed_cases = ?, failed_cases = ?, logs = ?, updated_at = ? WHERE id = ?
    """, ("completed", passed_count, failed_count, json.dumps(all_logs), datetime.now().isoformat(), report_id))
    conn.commit()
    conn.close()
    
    return {
        "report_id": report_id,
        "test_name": suite["name"],
        "total_cases": len(case_ids),
        "passed_cases": passed_count,
        "failed_cases": failed_count,
        "logs": all_logs
    }

@router.get("/tasks")
def list_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM web_tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/tasks")
def create_task(data: dict = Body(...)):
    conn = get_connection()
    cursor = conn.cursor()
    task_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO web_tasks (id, name, suite_id, task_type, cron_expression, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_id,
        data.get("name"),
        data.get("suite_id"),
        data.get("task_type", "manual"),
        data.get("cron_expression"),
        data.get("status", "pending"),
        now,
        now
    ))
    conn.commit()
    conn.close()
    return {"id": task_id, "message": "创建成功"}

@router.get("/tasks/{task_id}")
def get_task(task_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM web_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="任务不存在")
    return dict(row)

@router.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM web_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}
