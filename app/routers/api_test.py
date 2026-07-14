from fastapi import APIRouter, HTTPException, Body, Depends
from app.database import get_connection
from app.dependencies.auth import get_current_user
import json
import uuid
from datetime import datetime
import requests

router = APIRouter(prefix="/api/v1/api-test", tags=["接口测试"])

@router.get("/interfaces")
def list_interfaces(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_interfaces WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/interfaces")
def create_interface(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    interface_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO api_interfaces (id, user_id, name, url, method, headers, params, body, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        interface_id,
        current_user["id"],
        data.get("name"),
        data.get("url"),
        data.get("method", "GET"),
        json.dumps(data.get("headers", {})),
        json.dumps(data.get("params", {})),
        json.dumps(data.get("body", {})),
        data.get("description"),
        now,
        now
    ))
    conn.commit()
    conn.close()
    return {"id": interface_id, "message": "创建成功"}

@router.get("/interfaces/{interface_id}")
def get_interface(interface_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_interfaces WHERE id = ? AND user_id = ?", (interface_id, current_user["id"]))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="接口不存在")
    result = dict(row)
    result["headers"] = json.loads(result.get("headers", "{}"))
    result["params"] = json.loads(result.get("params", "{}"))
    result["body"] = json.loads(result.get("body", "{}"))
    return result

@router.put("/interfaces/{interface_id}")
def update_interface(interface_id: str, data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if "name" in data:
        updates.append("name = ?")
        params.append(data["name"])
    if "url" in data:
        updates.append("url = ?")
        params.append(data["url"])
    if "method" in data:
        updates.append("method = ?")
        params.append(data["method"])
    if "headers" in data:
        updates.append("headers = ?")
        params.append(json.dumps(data["headers"]))
    if "params" in data:
        updates.append("params = ?")
        params.append(json.dumps(data["params"]))
    if "body" in data:
        updates.append("body = ?")
        params.append(json.dumps(data["body"]))
    if "description" in data:
        updates.append("description = ?")
        params.append(data["description"])
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(interface_id)
        params.append(current_user["id"])
        cursor.execute(f"UPDATE api_interfaces SET {', '.join(updates)} WHERE id = ? AND user_id = ?", params)
        conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/interfaces/{interface_id}")
def delete_interface(interface_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM api_interfaces WHERE id = ? AND user_id = ?", (interface_id, current_user["id"]))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.post("/interfaces/{interface_id}/run")
def run_interface(interface_id: str, data: dict = Body({}), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_interfaces WHERE id = ? AND user_id = ?", (interface_id, current_user["id"]))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    interface = dict(row)
    headers = json.loads(interface.get("headers", "{}"))
    params = json.loads(interface.get("params", "{}"))
    body = json.loads(interface.get("body", "{}"))
    
    headers.update(data.get("headers", {}))
    params.update(data.get("params", {}))
    
    try:
        response = requests.request(
            method=interface["method"],
            url=interface["url"],
            headers=headers,
            params=params,
            json=body,
            timeout=30
        )
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios")
def list_scenarios(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_scenarios WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/scenarios")
def create_scenario(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    scenario_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO api_scenarios (id, user_id, name, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (scenario_id, current_user["id"], data.get("name"), data.get("description"), now, now))
    conn.commit()
    conn.close()
    return {"id": scenario_id, "message": "创建成功"}

@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_scenarios WHERE id = ? AND user_id = ?", (scenario_id, current_user["id"]))
    scenario = cursor.fetchone()
    if not scenario:
        conn.close()
        raise HTTPException(status_code=404, detail="场景不存在")
    
    cursor.execute("""
        SELECT s.*, i.name as interface_name 
        FROM api_scene_steps s 
        LEFT JOIN api_interfaces i ON s.interface_id = i.id 
        WHERE s.scenario_id = ? AND s.user_id = ?
        ORDER BY s.step_order
    """, (scenario_id, current_user["id"]))
    steps = cursor.fetchall()
    conn.close()
    
    result = dict(scenario)
    result["steps"] = []
    for step in steps:
        step_dict = dict(step)
        step_dict["request_data"] = json.loads(step_dict.get("request_data", "{}"))
        step_dict["extract_vars"] = json.loads(step_dict.get("extract_vars", "{}"))
        step_dict["assertions"] = json.loads(step_dict.get("assertions", "{}"))
        result["steps"].append(step_dict)
    
    return result

@router.put("/scenarios/{scenario_id}")
def update_scenario(scenario_id: str, data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if "name" in data:
        updates.append("name = ?")
        params.append(data["name"])
    if "description" in data:
        updates.append("description = ?")
        params.append(data["description"])
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(scenario_id)
        params.append(current_user["id"])
        cursor.execute(f"UPDATE api_scenarios SET {', '.join(updates)} WHERE id = ? AND user_id = ?", params)
        conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/scenarios/{scenario_id}")
def delete_scenario(scenario_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM api_scene_steps WHERE scenario_id = ? AND user_id = ?", (scenario_id, current_user["id"]))
    cursor.execute("DELETE FROM api_scenarios WHERE id = ? AND user_id = ?", (scenario_id, current_user["id"]))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.post("/scenarios/{scenario_id}/steps")
def add_scenario_step(scenario_id: str, data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_scenarios WHERE id = ? AND user_id = ?", (scenario_id, current_user["id"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="场景不存在")
    
    cursor.execute("SELECT MAX(step_order) FROM api_scene_steps WHERE scenario_id = ? AND user_id = ?", (scenario_id, current_user["id"]))
    max_order = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        INSERT INTO api_scene_steps (user_id, scenario_id, interface_id, step_order, request_data, extract_vars, assertions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user["id"],
        scenario_id,
        data.get("interface_id"),
        max_order + 1,
        json.dumps(data.get("request_data", {})),
        json.dumps(data.get("extract_vars", {})),
        json.dumps(data.get("assertions", {}))
    ))
    conn.commit()
    conn.close()
    return {"message": "添加成功"}

@router.put("/scenarios/{scenario_id}/steps/{step_id}")
def update_scenario_step(scenario_id: str, step_id: str, data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if "interface_id" in data:
        updates.append("interface_id = ?")
        params.append(data["interface_id"])
    if "request_data" in data:
        updates.append("request_data = ?")
        params.append(json.dumps(data["request_data"]))
    if "extract_vars" in data:
        updates.append("extract_vars = ?")
        params.append(json.dumps(data["extract_vars"]))
    if "assertions" in data:
        updates.append("assertions = ?")
        params.append(json.dumps(data["assertions"]))
    if updates:
        params.append(scenario_id)
        params.append(step_id)
        params.append(current_user["id"])
        cursor.execute(f"UPDATE api_scene_steps SET {', '.join(updates)} WHERE scenario_id = ? AND id = ? AND user_id = ?", params)
        conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/scenarios/{scenario_id}/steps/{step_id}")
def delete_scenario_step(scenario_id: str, step_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM api_scene_steps WHERE scenario_id = ? AND id = ? AND user_id = ?", (scenario_id, step_id, current_user["id"]))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.post("/scenarios/{scenario_id}/run")
def run_scenario(scenario_id: str, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM api_scenarios WHERE id = ? AND user_id = ?", (scenario_id, current_user["id"]))
    scenario = cursor.fetchone()
    if not scenario:
        conn.close()
        raise HTTPException(status_code=404, detail="场景不存在")
    
    cursor.execute("""
        SELECT s.*, i.name as interface_name, i.url, i.method, i.headers, i.params, i.body 
        FROM api_scene_steps s 
        LEFT JOIN api_interfaces i ON s.interface_id = i.id 
        WHERE s.scenario_id = ? AND s.user_id = ?
        ORDER BY s.step_order
    """, (scenario_id, current_user["id"]))
    steps = cursor.fetchall()
    
    report_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO reports (id, user_id, test_type, test_name, status, total_cases, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (report_id, current_user["id"], "api", scenario["name"], "running", len(steps), now, now))
    conn.commit()
    
    results = []
    variables = {}
    passed_count = 0
    failed_count = 0
    
    for idx, step in enumerate(steps):
        step_dict = dict(step)
        step_result = {
            "step_index": idx + 1,
            "interface_name": step_dict["interface_name"],
            "request_url": step_dict["url"],
            "request_method": step_dict["method"]
        }
        
        headers = json.loads(step_dict.get("headers", "{}"))
        params = json.loads(step_dict.get("params", "{}"))
        body = json.loads(step_dict.get("body", "{}"))
        request_data = json.loads(step_dict.get("request_data", "{}"))
        extract_vars = json.loads(step_dict.get("extract_vars", "{}"))
        assertions = json.loads(step_dict.get("assertions", "{}"))
        
        headers.update(request_data.get("headers", {}))
        params.update(request_data.get("params", {}))
        
        try:
            response = requests.request(
                method=step_dict["method"],
                url=step_dict["url"],
                headers=headers,
                params=params,
                json=body,
                timeout=30
            )
            
            step_result["response_status"] = response.status_code
            step_result["response_time"] = response.elapsed.total_seconds()
            
            try:
                response_body = response.json()
            except:
                response_body = response.text
            step_result["response_body"] = response_body
            
            passed = True
            error_messages = []
            
            for assertion in assertions:
                assert_type = assertion.get("type", "status_code")
                expected = assertion.get("expected")
                
                if assert_type == "status_code":
                    if response.status_code != expected:
                        passed = False
                        error_messages.append(f"状态码断言失败：期望 {expected}，实际 {response.status_code}")
                
                elif assert_type == "json_path":
                    json_path = assertion.get("json_path")
                    try:
                        value = response_body
                        for key in json_path.split('.'):
                            value = value[key]
                        if value != expected:
                            passed = False
                            error_messages.append(f"JSON断言失败：{json_path} 期望 {expected}，实际 {value}")
                    except Exception as e:
                        passed = False
                        error_messages.append(f"JSON路径解析失败：{e}")
            
            step_result["passed"] = passed
            step_result["error_message"] = "; ".join(error_messages)
            
            if passed:
                passed_count += 1
            else:
                failed_count += 1
            
            for var_name, json_path in extract_vars.items():
                try:
                    value = response_body
                    for key in json_path.split('.'):
                        value = value[key]
                    variables[var_name] = value
                except:
                    pass
            
            results.append(step_result)
            
            result_id = str(uuid.uuid4())[:8]
            cursor.execute("""
                INSERT INTO api_test_results (id, report_id, scenario_id, step_index, interface_name,
                    request_url, request_method, response_status, response_time, assertions, passed, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result_id, report_id, scenario_id, idx + 1, step_dict["interface_name"],
                step_dict["url"], step_dict["method"], response.status_code,
                response.elapsed.total_seconds(), json.dumps(assertions), passed,
                "; ".join(error_messages), now
            ))
            conn.commit()
            
        except Exception as e:
            step_result["passed"] = False
            step_result["error_message"] = str(e)
            failed_count += 1
            results.append(step_result)
    
    cursor.execute("""
        UPDATE reports SET status = ?, passed_cases = ?, failed_cases = ?, updated_at = ? WHERE id = ?
    """, ("completed", passed_count, failed_count, datetime.now().isoformat(), report_id))
    conn.commit()
    conn.close()
    
    return {
        "report_id": report_id,
        "test_name": scenario["name"],
        "total_cases": len(steps),
        "passed_cases": passed_count,
        "failed_cases": failed_count,
        "results": results
    }

@router.get("/envs")
def list_envs(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_envs WHERE user_id = ? ORDER BY created_at DESC", (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/envs")
def create_env(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    env_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO api_envs (id, user_id, name, base_url, variables, is_default, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        env_id,
        current_user["id"],
        data.get("name"),
        data.get("base_url"),
        json.dumps(data.get("variables", {})),
        data.get("is_default", 0),
        now
    ))
    conn.commit()
    conn.close()
    return {"id": env_id, "message": "创建成功"}
