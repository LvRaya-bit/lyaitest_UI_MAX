from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from app.database import get_connection
from app.dependencies.auth import get_current_user
from app.storage import save_uploaded_file, get_uploaded_file_path
import json
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/knowledge-base", tags=["知识库"])

@router.get("/")
def list_knowledge_bases(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_bases WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/")
def create_knowledge_base(name: str = Form(...), description: str = Form(None), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    kb_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO knowledge_bases (id, user_id, name, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (kb_id, current_user["id"], name, description, now, now))
    conn.commit()
    conn.close()
    return {"id": kb_id, "name": name, "description": description}

@router.get("/{kb_id}")
def get_knowledge_base(kb_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_bases WHERE id = ? AND user_id = ?", (kb_id, current_user["id"]))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return dict(row)

@router.put("/{kb_id}")
def update_knowledge_base(kb_id: str, name: str = Form(None), description: str = Form(None), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if name:
        updates.append("name = ?")
        params.append(name)
    if description:
        updates.append("description = ?")
        params.append(description)
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(kb_id)
        params.append(current_user["id"])
        cursor.execute(f"UPDATE knowledge_bases SET {', '.join(updates)} WHERE id = ? AND user_id = ?", params)
        conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/{kb_id}")
def delete_knowledge_base(kb_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE knowledge_base_id = ? AND user_id = ?", (kb_id, current_user["id"]))
    cursor.execute("DELETE FROM knowledge_bases WHERE id = ? AND user_id = ?", (kb_id, current_user["id"]))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.get("/{kb_id}/documents")
def list_documents(kb_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE knowledge_base_id = ? AND user_id = ? ORDER BY created_at DESC", (kb_id, current_user["id"]))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/{kb_id}/documents")
async def upload_document(kb_id: str, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_bases WHERE id = ? AND user_id = ?", (kb_id, current_user["id"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="知识库不存在")

    file_path = await save_uploaded_file(file)
    doc_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    file_type = file.filename.split('.')[-1].lower()

    content = ""
    if file_type in ['txt', 'md', 'markdown']:
        abs_path = get_uploaded_file_path(file_path)
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取文件内容失败: {e}")

    cursor.execute("""
        INSERT INTO documents (id, user_id, knowledge_base_id, filename, file_path, file_type, content, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (doc_id, current_user["id"], kb_id, file.filename, file_path, file_type, content, now, now))
    conn.commit()
    conn.close()
    return {"id": doc_id, "filename": file.filename, "file_type": file_type}

@router.get("/{kb_id}/documents/{doc_id}")
def get_document(kb_id: str, doc_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ? AND knowledge_base_id = ? AND user_id = ?", (doc_id, kb_id, current_user["id"]))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="文档不存在")
    return dict(row)

@router.get("/{kb_id}/documents/{doc_id}/download")
def download_document(kb_id: str, doc_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ? AND knowledge_base_id = ? AND user_id = ?", (doc_id, kb_id, current_user["id"]))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="文档不存在")
    file_path = get_uploaded_file_path(row["file_path"])
    return FileResponse(file_path, filename=row["filename"])

@router.delete("/{kb_id}/documents/{doc_id}")
def delete_document(kb_id: str, doc_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ? AND knowledge_base_id = ? AND user_id = ?", (doc_id, kb_id, current_user["id"]))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}
