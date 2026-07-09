from fastapi import FastAPI
from app.routers import chat, sessions, agent  # sessions 必须在这里

app = FastAPI(
    title="LYAITEST AI测试平台",
    description="AI驱动的测试智能体平台",
    version="0.1.0"
)

app.include_router(chat.router)
app.include_router(sessions.router)  # 必须加上这一行
app.include_router(agent.router) 

@app.get("/")
def root():
    return {"message": "Hello from LYAITEST"}

@app.get("/health")
def health():
    return {"status": "ok"}