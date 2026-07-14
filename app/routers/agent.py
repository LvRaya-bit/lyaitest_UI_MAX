from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.agent import run_agent
from app.database import get_connection
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

class AgentRequest(BaseModel):
    message: str
    session_id: str
    knowledge_base_id: Optional[str] = None
    interface_id: Optional[str] = None
    web_case_id: Optional[str] = None

class AgentResponse(BaseModel):
    reply: str

@router.post("/", response_model=AgentResponse)
async def agent_chat(request: AgentRequest, current_user: dict = Depends(get_current_user)):
    try:
        kb_id = request.knowledge_base_id
        if not kb_id:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT knowledge_base_id FROM sessions WHERE session_id = ? AND user_id = ?", (request.session_id, current_user["id"]))
            row = cursor.fetchone()
            conn.close()
            if row:
                kb_id = row["knowledge_base_id"]

        result = run_agent(
            request.message, request.session_id, kb_id,
            request.interface_id, request.web_case_id,
            user_id=current_user["id"]
        )
        return AgentResponse(reply=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
