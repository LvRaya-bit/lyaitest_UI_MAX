from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_connection
from app.dependencies.auth import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

class SessionCreate(BaseModel):
    name: Optional[str] = None
    knowledge_base_id: Optional[str] = None

class SessionUpdate(BaseModel):
    name: Optional[str] = None
    knowledge_base_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    name: str
    created_at: str
    knowledge_base_id: Optional[str] = None

class MessageResponse(BaseModel):
    role: str
    content: str

@router.post("/", response_model=SessionResponse)
async def create_session(request: SessionCreate, current_user: dict = Depends(get_current_user)):
    session_id = str(uuid.uuid4())[:8]
    name = request.name or f"会话_{session_id}"
    now = datetime.now().isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (session_id, user_id, name, session_type, knowledge_base_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, current_user["id"], name, "normal", request.knowledge_base_id, now, now))
    conn.commit()
    conn.close()
    
    return SessionResponse(
        session_id=session_id,
        name=name,
        created_at=now,
        knowledge_base_id=request.knowledge_base_id
    )

@router.get("/", response_model=List[SessionResponse])
async def list_sessions(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [SessionResponse(
        session_id=row["session_id"],
        name=row["name"],
        created_at=row["created_at"],
        knowledge_base_id=row["knowledge_base_id"]
    ) for row in rows]

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ? AND user_id = ?", (session_id, current_user["id"]))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在")
    return SessionResponse(
        session_id=row["session_id"],
        name=row["name"],
        created_at=row["created_at"],
        knowledge_base_id=row["knowledge_base_id"]
    )

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, request: SessionUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ? AND user_id = ?", (session_id, current_user["id"]))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="会话不存在")

    updates = []
    params = []
    if request.name is not None:
        updates.append("name = ?")
        params.append(request.name)
    if request.knowledge_base_id is not None:
        updates.append("knowledge_base_id = ?")
        params.append(request.knowledge_base_id)
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(session_id)
        params.append(current_user["id"])
        cursor.execute(f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ? AND user_id = ?", params)
        conn.commit()

    cursor.execute("SELECT * FROM sessions WHERE session_id = ? AND user_id = ?", (session_id, current_user["id"]))
    updated = cursor.fetchone()
    conn.close()
    return SessionResponse(
        session_id=updated["session_id"],
        name=updated["name"],
        created_at=updated["created_at"],
        knowledge_base_id=updated["knowledge_base_id"]
    )

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(session_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE session_id = ? AND user_id = ? ORDER BY created_at ASC", (session_id, current_user["id"]))
    rows = cursor.fetchall()
    conn.close()
    return [MessageResponse(role=row["role"], content=row["content"]) for row in rows]

@router.delete("/{session_id}")
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ? AND user_id = ?", (session_id, current_user["id"]))
    cursor.execute("DELETE FROM sessions WHERE session_id = ? AND user_id = ?", (session_id, current_user["id"]))
    conn.commit()
    conn.close()
    return {"message": "会话已删除"}
