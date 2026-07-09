# app/routers/agent.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.agent import run_agent

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

class AgentRequest(BaseModel):
    message: str

class AgentResponse(BaseModel):
    reply: str

@router.post("/", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):
    try:
        result = run_agent(request.message)
        return AgentResponse(reply=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))