from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, sessions, agent, report, knowledge_base, api_test, web_automation, auth
from app.database import init_db

init_db()

app = FastAPI(
    title="LYAITEST AI测试平台",
    description="AI驱动的测试智能体平台",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(agent.router)
app.include_router(report.router)
app.include_router(knowledge_base.router)
app.include_router(api_test.router)
app.include_router(web_automation.router)

@app.get("/")
def root():
    return {"message": "Hello from LYAITEST"}

@app.get("/health")
def health():
    return {"status": "ok"}
