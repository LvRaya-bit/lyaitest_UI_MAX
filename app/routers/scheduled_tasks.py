from fastapi import APIRouter, HTTPException, Body
from app.database import get_connection
import json
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/scheduled-tasks", tags=["定时任务"])

@router.get("/")
def list_scheduled_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scheduled_tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/")
def create_scheduled_task(data: dict = Body(...)):
    conn = get_connection()
    cursor = conn.cursor()
    task_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO scheduled_tasks (id, name, task_type, target_id, cron_expression, params, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_id,
        data.get("name"),
        data.get("task_type"),
        data.get("target_id"),
        data.get("cron_expression"),
        json.dumps(data.get("params", {})),
        data.get("status", "enabled"),
        now,
        now
    ))
    conn.commit()
    conn.close()
    return {"id": task_id, "message": "创建成功"}

@router.get("/{task_id}")
def get_scheduled_task(task_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scheduled_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    result = dict(row)
    result["params"] = json.loads(result.get("params", "{}"))
    return result

@router.put("/{task_id}")
def update_scheduled_task(task_id: str, data: dict = Body(...)):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if "name" in data:
        updates.append("name = ?")
        params.append(data["name"])
    if "task_type" in data:
        updates.append("task_type = ?")
        params.append(data["task_type"])
    if "target_id" in data:
        updates.append("target_id = ?")
        params.append(data["target_id"])
    if "cron_expression" in data:
        updates.append("cron_expression = ?")
        params.append(data["cron_expression"])
    if "params" in data:
        updates.append("params = ?")
        params.append(json.dumps(data["params"]))
    if "status" in data:
        updates.append("status = ?")
        params.append(data["status"])
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(task_id)
        cursor.execute(f"UPDATE scheduled_tasks SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/{task_id}")
def delete_scheduled_task(task_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.post("/{task_id}/run")
def trigger_scheduled_task(task_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scheduled_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    task = dict(row)
    task["params"] = json.loads(task.get("params", "{}"))
    
    now = datetime.now().isoformat()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE scheduled_tasks SET last_run_at = ? WHERE id = ?
    """, (now, task_id))
    conn.commit()
    conn.close()
    
    return {"message": "任务已触发", "task": task, "triggered_at": now}
