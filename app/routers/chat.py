from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
import asyncio

load_dotenv()

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0.3
)

# ========== 普通接口（一次性返回） ==========
@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = llm.invoke(request.message)
        return ChatResponse(reply=response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== 流式接口（逐字返回） ==========
@router.post("/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        # 流式调用 LangChain，逐字返回
        async for chunk in llm.astream(request.message):
            # SSE 格式要求：每个数据块以 "data: " 开头，并以两个换行符结束
            yield f"data: {chunk.content}\n\n"
    
    # 使用 text/event-stream 媒体类型，符合 SSE 标准
    return StreamingResponse(generate(), media_type="text/event-stream")