from pydantic import BaseModel
from typing import Optional

class TestReport(BaseModel):
    id: str
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    test_type: str
    test_name: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    title: Optional[str] = None
    screenshot: Optional[str] = None
    error: Optional[str] = None
    status: str = "completed"
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    duration: Optional[float] = None
    logs: Optional[str] = None
    created_at: str = ""
    updated_at: Optional[str] = None
