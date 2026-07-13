from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_connection
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

class SessionCreate(BaseModel):
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
async def create_session(request: SessionCreate):
    session_id = str(uuid.uuid4())[:8]
    name = request.name or f"会话_{session_id}"
    now = datetime.now().isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (session_id, name, session_type, knowledge_base_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, name, "normal", request.knowledge_base_id, now, now))
    conn.commit()
    conn.close()
    
    return SessionResponse(
        session_id=session_id,
        name=name,
        created_at=now,
        knowledge_base_id=request.knowledge_base_id
    )

@router.get("/", response_model=List[SessionResponse])
async def list_sessions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [SessionResponse(
        session_id=row["session_id"],
        name=row["name"],
        created_at=row["created_at"],
        knowledge_base_id=row["knowledge_base_id"]
    ) for row in rows]

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
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

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [MessageResponse(role=row["role"], content=row["content"]) for row in rows]

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"message": "会话已删除"}
