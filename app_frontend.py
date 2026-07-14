import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="LYAITEST AI测试平台", page_icon="🤖", layout="wide")

API_BASE = st.secrets.get("api_base", os.getenv("API_BASE", "http://localhost:8001/api/v1"))

# ============================================
# 初始化会话状态
# ============================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "ai_assistant"
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "knowledge_bases" not in st.session_state:
    st.session_state.knowledge_bases = []
if "interfaces" not in st.session_state:
    st.session_state.interfaces = []
if "web_cases" not in st.session_state:
    st.session_state.web_cases = []
if "selected_interface_id" not in st.session_state:
    st.session_state.selected_interface_id = None
if "selected_web_case_id" not in st.session_state:
    st.session_state.selected_web_case_id = None
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "login_tab" not in st.session_state:
    st.session_state.login_tab = "login"

# ============================================
# 工具函数（带Token认证）
# ============================================
def clear_user_cache():
    """清除所有用户相关的业务缓存，用于切换用户时避免数据串号"""
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.sessions = []
    st.session_state.knowledge_bases = []
    st.session_state.interfaces = []
    st.session_state.web_cases = []
    st.session_state.selected_interface_id = None
    st.session_state.selected_web_case_id = None
    if "selected_kb" in st.session_state:
        st.session_state.selected_kb = None
    if "case_steps" in st.session_state:
        st.session_state.case_steps = []

def get_headers():
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers

def fetch_data(endpoint):
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", headers=get_headers())
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()
        return []
    except:
        return []

def call_api(method, endpoint, data=None, form_data=None, files=None):
    try:
        url = f"{API_BASE}/{endpoint}"
        headers = get_headers()
        if method == "POST":
            if files:
                r = requests.post(url, files=files, headers=headers)
            elif form_data:
                r = requests.post(url, data=form_data, headers=headers)
            else:
                r = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            r = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers)
        else:
            r = requests.get(url, headers=headers)
        if r.status_code == 401:
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()
        return r
    except Exception as e:
        return None

# ============================================
# 页面：登录/注册
# ============================================
def render_login():
    st.title("🔐 LYAITEST AI测试平台")
    st.subheader("用户认证")

    tab_login, tab_register = st.tabs(["登录", "注册"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("登录", use_container_width=True, type="primary")

        if submitted:
            if username and password:
                with st.spinner("登录中..."):
                    try:
                        r = requests.post(f"{API_BASE}/auth/login", data={
                            "username": username,
                            "password": password
                        })
                        if r.status_code == 200:
                            result = r.json()
                            clear_user_cache()
                            st.session_state.token = result["access_token"]
                            st.session_state.username = result["username"]
                            st.session_state.user_id = result["user_id"]
                            st.success(f"🎉 欢迎回来，{username}!")
                            st.rerun()
                        else:
                            st.error("用户名或密码错误")
                    except Exception as e:
                        st.error(f"登录失败: {e}")
            else:
                st.warning("请输入用户名和密码")

    with tab_register:
        with st.form("register_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            confirm_password = st.text_input("确认密码", type="password")
            submitted = st.form_submit_button("注册", use_container_width=True, type="primary")

        if submitted:
            if username and password and confirm_password:
                if password == confirm_password:
                    with st.spinner("注册中..."):
                        try:
                            r = requests.post(f"{API_BASE}/auth/register", json={
                                "username": username,
                                "password": password
                            })
                            if r.status_code == 200:
                                st.success("✅ 注册成功，请登录")
                            else:
                                st.error(r.json().get("detail", "注册失败"))
                        except Exception as e:
                            st.error(f"注册失败: {e}")
                else:
                    st.warning("两次密码不一致")
            else:
                st.warning("请填写所有字段")

    st.divider()
    st.caption("v0.3.0 | 对标MSAITest")

# ============================================
# 侧边栏导航
# ============================================
def render_sidebar():
    with st.sidebar:
        st.title("LYAITEST AI测试平台")
        st.divider()

        menus = [
            {"id": "ai_assistant", "name": "🤖 AI助手中心"},
            {"id": "knowledge_base", "name": "📚 项目知识库"},
            {"id": "api_test", "name": "🔌 接口测试"},
            {"id": "web_automation", "name": "🌐 Web自动化"},
            {"id": "test_reports", "name": "📊 测试报告"},
            {"id": "user_management", "name": "👥 用户管理"},
        ]
        for item in menus:
            if st.button(item["name"], key=f"menu_{item['id']}", use_container_width=True,
                         type="primary" if st.session_state.current_page == item['id'] else "secondary"):
                st.session_state.current_page = item["id"]
                st.rerun()

        st.divider()
        if st.session_state.username:
            st.write(f"当前用户: {st.session_state.username}")
            if st.button("退出登录", use_container_width=True):
                clear_user_cache()
                st.session_state.token = None
                st.session_state.username = None
                st.session_state.user_id = None
                st.rerun()
        st.caption("v0.3.0 | 对标MSAITest")

# ============================================
# 页面：AI助手中心
# ============================================
def render_ai_assistant():
    st.title("🤖 AI助手中心")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("📂 会话管理")

        st.session_state.knowledge_bases = fetch_data("knowledge-base/")

        with st.form("create_session_form"):
            session_name = st.text_input("会话名称")
            kb_options = ["不绑定知识库"] + [f"{kb['name']} (id:{kb['id']})" for kb in st.session_state.knowledge_bases]
            selected_kb = st.selectbox("关联知识库", kb_options, help="绑定后AI对话将自动检索知识库文档")
            submitted = st.form_submit_button("创建会话", use_container_width=True)

        if submitted:
            if session_name:
                kb_id = None
                if selected_kb != "不绑定知识库":
                    for kb in st.session_state.knowledge_bases:
                        if kb["id"] in selected_kb:
                            kb_id = kb["id"]
                            break
                data = {"name": session_name}
                if kb_id:
                    data["knowledge_base_id"] = kb_id
                r = call_api("POST", "sessions/", data)
                if r and r.status_code == 200:
                    st.success("会话创建成功")
                    st.session_state.sessions = fetch_data("sessions/")
                    st.session_state.session_id = r.json()["session_id"]
                    st.session_state.messages = []
                else:
                    st.error("创建失败")
            else:
                st.warning("请输入会话名称")

        if st.button("刷新会话列表", use_container_width=True):
            st.session_state.sessions = fetch_data("sessions/")

        st.divider()

        for session in st.session_state.sessions:
            c_a, c_b = st.columns([3, 1])
            with c_a:
                kb_tag = " 📚" if session.get("knowledge_base_id") else ""
                if st.button(f"📌 {session['name']}{kb_tag}", key=f"sess_{session['session_id']}", use_container_width=True):
                    st.session_state.session_id = session["session_id"]
                    msgs = fetch_data(f"sessions/{session['session_id']}/messages")
                    st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in msgs]
            with c_b:
                if st.button("🗑️", key=f"del_{session['session_id']}"):
                    call_api("DELETE", f"sessions/{session['session_id']}")
                    st.session_state.sessions = fetch_data("sessions/")
                    if st.session_state.session_id == session["session_id"]:
                        st.session_state.session_id = None
                        st.session_state.messages = []
                    st.rerun()

    with col2:
        st.subheader("💬 对话窗口")

        if st.session_state.session_id is None:
            st.info("👈 请先创建或选择一个会话")
            st.markdown("""
            **AI助手支持以下指令：**
            - 📋 "帮我生成登录功能的测试用例" — 基于知识库生成用例
            - 🧪 "执行接口测试" — 调用已录入的接口执行
            - 🌐 "运行Web自动化" — 执行已录入的Web用例
            - 📊 "查询测试报告" — 汇总历史执行结果

            **也可通过下方选择器选择接口/Web用例后点击执行按钮。**
            """)
        else:
            current_session = next((s for s in st.session_state.sessions if s["session_id"] == st.session_state.session_id), None)
            if current_session and current_session.get("knowledge_base_id"):
                kb_name = next((kb["name"] for kb in st.session_state.knowledge_bases if kb["id"] == current_session["knowledge_base_id"]), "未知")
                st.info(f"📚 当前会话已绑定知识库: {kb_name}")

            st.session_state.interfaces = fetch_data("api-test/interfaces")
            st.session_state.web_cases = fetch_data("web-automation/cases")

            with st.expander("🎯 测试素材选择器（选择后点击执行按钮）", expanded=False):
                sel_col1, sel_col2, exec_col1, exec_col2 = st.columns(4)

                with sel_col1:
                    if_options = ["不选择"] + [f"{i['name']} (id:{i['id']})" for i in st.session_state.interfaces]
                    sel_if = st.selectbox("选择接口", if_options, key="sel_if")
                    if sel_if != "不选择":
                        st.session_state.selected_interface_id = sel_if.split("id:")[1].rstrip(")")
                    else:
                        st.session_state.selected_interface_id = None

                with exec_col1:
                    if st.button("🧪 执行接口", use_container_width=True, disabled=not st.session_state.selected_interface_id):
                        if st.session_state.selected_interface_id:
                            with st.spinner("正在执行接口..."):
                                r = call_api("POST", "agent/", {
                                    "message": "执行选中的接口",
                                    "session_id": st.session_state.session_id,
                                    "interface_id": st.session_state.selected_interface_id
                                })
                            if r and r.status_code == 200:
                                reply = r.json().get("reply", "执行失败")
                                st.session_state.messages.append({"role": "user", "content": "🧪 执行选中接口"})
                                st.session_state.messages.append({"role": "assistant", "content": reply})
                                st.rerun()
                            else:
                                st.error("执行请求失败")

                with sel_col2:
                    wc_options = ["不选择"] + [f"{c['name']} (id:{c['id']})" for c in st.session_state.web_cases]
                    sel_wc = st.selectbox("选择Web用例", wc_options, key="sel_wc")
                    if sel_wc != "不选择":
                        st.session_state.selected_web_case_id = sel_wc.split("id:")[1].rstrip(")")
                    else:
                        st.session_state.selected_web_case_id = None

                with exec_col2:
                    if st.button("🌐 执行Web用例", use_container_width=True, disabled=not st.session_state.selected_web_case_id):
                        if st.session_state.selected_web_case_id:
                            with st.spinner("正在执行Web自动化..."):
                                r = call_api("POST", "agent/", {
                                    "message": "执行选中的Web用例",
                                    "session_id": st.session_state.session_id,
                                    "web_case_id": st.session_state.selected_web_case_id
                                })
                            if r and r.status_code == 200:
                                reply = r.json().get("reply", "执行失败")
                                st.session_state.messages.append({"role": "user", "content": "🌐 执行选中Web用例"})
                                st.session_state.messages.append({"role": "assistant", "content": reply})
                                st.rerun()
                            else:
                                st.error("执行请求失败")

            st.divider()

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            user_input = st.chat_input("输入消息，AI将根据知识库和测试资源智能响应...")
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.write(user_input)

                with st.chat_message("assistant"):
                    with st.spinner("AI正在分析并调用平台资源..."):
                        r = call_api("POST", "agent/", {
                            "message": user_input,
                            "session_id": st.session_state.session_id
                        })
                    if r and r.status_code == 200:
                        reply = r.json().get("reply", "抱歉，处理失败")
                        st.write(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    else:
                        st.error("AI请求失败")


# ============================================
# 页面：项目知识库
# ============================================
def render_knowledge_base():
    st.title("📚 项目知识库")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("知识库管理")

        with st.form("create_kb_form"):
            kb_name = st.text_input("知识库名称")
            kb_desc = st.text_area("描述")
            submitted = st.form_submit_button("创建知识库", use_container_width=True)

        if submitted:
            if kb_name:
                r = call_api("POST", "knowledge-base/", form_data={"name": kb_name, "description": kb_desc})
                if r and r.status_code == 200:
                    st.success("✅ 知识库创建成功")
                    st.session_state.knowledge_bases = fetch_data("knowledge-base/")
                else:
                    st.error(f"创建失败: {r.status_code if r else '无响应'}")
            else:
                st.warning("请输入知识库名称")

        if st.button("刷新列表", use_container_width=True):
            st.session_state.knowledge_bases = fetch_data("knowledge-base/")
            st.rerun()

        st.divider()

        for kb in st.session_state.knowledge_bases:
            if st.button(f"📖 {kb['name']}", key=f"kb_{kb['id']}", use_container_width=True):
                st.session_state.selected_kb = kb["id"]
                st.rerun()

    with col2:
        if "selected_kb" in st.session_state and st.session_state.selected_kb:
            kb = next((k for k in st.session_state.knowledge_bases if k["id"] == st.session_state.selected_kb), None)
            if kb:
                st.subheader(f"📄 {kb['name']}")
                if kb.get("description"):
                    st.caption(kb["description"])

                st.divider()
                st.write("**知识库信息**")
                st.write(f"- **ID**: {kb['id']}")
                st.write(f"- **创建时间**: {kb['created_at'][:19]}")

                st.divider()
                st.write("**📁 文档管理**")

                with st.form("upload_doc_form"):
                    uploaded_file = st.file_uploader("上传文档", type=["txt", "md", "markdown"])
                    if st.form_submit_button("📤 上传文档", use_container_width=True):
                        if uploaded_file:
                            with st.spinner("正在上传..."):
                                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                                try:
                                    r = call_api("POST", f"knowledge-base/{kb['id']}/documents", files=files)
                                    if r and r.status_code == 200:
                                        st.success(f"✅ 文档 {uploaded_file.name} 上传成功")
                                    else:
                                        st.error(f"上传失败: {r.status_code if r else '无响应'}")
                                except Exception as e:
                                    st.error(f"上传失败: {e}")

                st.divider()
                st.write("**文档列表**")
                docs = fetch_data(f"knowledge-base/{kb['id']}/documents")
                if docs:
                    for doc in docs:
                        c1, c2, c3 = st.columns([3, 2, 1])
                        with c1:
                            st.write(f"📄 {doc['filename']}")
                        with c2:
                            st.write(f"类型: {doc['file_type']} | {doc['created_at'][:19]}")
                        with c3:
                            if st.button("🗑️", key=f"del_doc_{doc['id']}"):
                                r = call_api("DELETE", f"knowledge-base/{kb['id']}/documents/{doc['id']}")
                                if r and r.status_code == 200:
                                    st.success("已删除")
                                    st.rerun()
                else:
                    st.info("暂无文档，请上传文档以丰富知识库内容")

                st.divider()
                st.write("**联动说明**")
                st.markdown("""
                - 在【AI助手中心】创建会话时可绑定此知识库
                - AI对话、生成用例时会自动检索绑定知识库的内容作为参考
                - 支持多个知识库隔离，不同项目独立使用
                """)
        else:
            st.info("👈 请选择或创建一个知识库")


# ============================================
# 页面：接口测试
# ============================================
def render_api_test():
    st.title("🔌 接口测试")

    st.info("📋 本页面仅用于维护接口素材。执行接口请前往【AI助手中心】通过对话或选择器发起。")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("新建接口")

        with st.form("create_interface_form"):
            interface_name = st.text_input("接口名称")
            interface_url = st.text_input("请求URL")
            method = st.selectbox("请求方法", ["GET", "POST", "PUT", "DELETE", "PATCH"])
            headers_input = st.text_area("Headers (JSON)", '{"Content-Type": "application/json"}')
            params_input = st.text_area("Params (JSON)", "{}")
            body_input = st.text_area("Body (JSON)", "{}")
            description = st.text_area("描述")
            submitted = st.form_submit_button("保存接口", use_container_width=True)

        if submitted:
            if interface_name and interface_url:
                try:
                    data = {
                        "name": interface_name, "url": interface_url, "method": method,
                        "headers": json.loads(headers_input), "params": json.loads(params_input),
                        "body": json.loads(body_input), "description": description
                    }
                    r = call_api("POST", "api-test/interfaces", data)
                    if r and r.status_code == 200:
                        st.success("✅ 接口保存成功")
                        st.session_state.interfaces = fetch_data("api-test/interfaces")
                    else:
                        st.error(f"保存失败: {r.status_code if r else '无响应'}")
                except json.JSONDecodeError:
                    st.error("JSON格式错误，请检查 Headers/Params/Body")
            else:
                st.warning("请填写接口名称和URL")

    with col2:
        st.subheader("接口列表")

        if st.button("刷新列表"):
            st.session_state.interfaces = fetch_data("api-test/interfaces")
            st.rerun()

        if st.session_state.interfaces:
            for interface in st.session_state.interfaces:
                with st.expander(f"🔗 {interface['name']} [{interface['method']}]"):
                    st.write(f"**URL**: {interface['url']}")
                    if interface.get("description"):
                        st.write(f"**描述**: {interface['description']}")
                    st.write(f"**ID**: {interface['id']}")
                    st.write(f"**创建时间**: {interface['created_at'][:19]}")

                    if st.button("🗑️ 删除", key=f"del_if_{interface['id']}"):
                        r = call_api("DELETE", f"api-test/interfaces/{interface['id']}")
                        if r and r.status_code == 200:
                            st.success("已删除")
                            st.session_state.interfaces = fetch_data("api-test/interfaces")
                            st.rerun()
        else:
            st.info("暂无接口，请在左侧创建")


# ============================================
# 页面：Web自动化
# ============================================
def render_web_automation():
    st.title("🌐 Web自动化")

    st.info("📋 本页面仅用于维护自动化用例素材。执行用例请前往【AI助手中心】通过对话或选择器发起。")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("新建用例")

        with st.form("create_case_form"):
            case_name = st.text_input("用例名称")
            case_desc = st.text_area("用例描述")
            submitted = st.form_submit_button("保存用例", use_container_width=True)

        if submitted:
            if case_name:
                if "case_steps" not in st.session_state:
                    st.session_state.case_steps = []
                data = {"name": case_name, "description": case_desc, "steps": st.session_state.case_steps}
                r = call_api("POST", "web-automation/cases", data)
                if r and r.status_code == 200:
                    st.success("✅ 用例保存成功")
                    st.session_state.case_steps = []
                    st.session_state.web_cases = fetch_data("web-automation/cases")
                else:
                    st.error(f"保存失败: {r.status_code if r else '无响应'}")
            else:
                st.warning("请填写用例名称")

        st.divider()
        st.subheader("步骤编辑器")

        with st.form("add_step_form"):
            action_type = st.selectbox("操作类型", ["navigate", "click", "input", "wait", "assert"])
            element_selector = st.text_input("元素选择器/CSS")
            element_value = st.text_input("输入值")
            expected_value = st.text_input("预期结果")
            add_submitted = st.form_submit_button("+ 添加步骤")

        if add_submitted:
            if "case_steps" not in st.session_state:
                st.session_state.case_steps = []
            st.session_state.case_steps.append({
                "action": action_type, "element": element_selector,
                "value": element_value, "expected": expected_value
            })
            st.success(f"已添加步骤 {len(st.session_state.case_steps)}")
            st.rerun()

        if "case_steps" in st.session_state and st.session_state.case_steps:
            st.write("**当前步骤：**")
            for idx, step in enumerate(st.session_state.case_steps):
                st.write(f"{idx+1}. `{step['action']}` → {step['element']} {step.get('value','')}")

            if st.button("清空步骤"):
                st.session_state.case_steps = []
                st.rerun()

    with col2:
        st.subheader("用例列表")

        if st.button("刷新列表"):
            st.session_state.web_cases = fetch_data("web-automation/cases")
            st.rerun()

        if st.session_state.web_cases:
            for case in st.session_state.web_cases:
                with st.expander(f"📋 {case['name']}"):
                    if case.get("description"):
                        st.write(f"**描述**: {case['description']}")
                    st.write(f"**ID**: {case['id']}")
                    steps = json.loads(case.get("steps", "[]"))
                    st.write(f"**步骤数**: {len(steps)}")
                    for s in steps:
                        st.write(f"  • `{s.get('action')}` {s.get('element','')} {s.get('value','')}")

                    if st.button("🗑️ 删除", key=f"del_case_{case['id']}"):
                        r = call_api("DELETE", f"web-automation/cases/{case['id']}")
                        if r and r.status_code == 200:
                            st.success("已删除")
                            st.session_state.web_cases = fetch_data("web-automation/cases")
                            st.rerun()
        else:
            st.info("暂无用例，请在左侧创建")


# ============================================
# 页面：测试报告
# ============================================
def render_test_reports():
    st.title("📊 测试报告")

    st.info("📋 本页面展示AI对话触发执行产生的运行记录。")

    reports = fetch_data("reports/")

    if not reports:
        st.info("暂无测试报告。在【AI助手中心】执行接口或Web用例后会自动生成报告。")
        return

    col1, col2, col3 = st.columns(3)
    total = len(reports)
    completed = len([r for r in reports if r.get("status") == "completed"])
    passed = sum(r.get("passed_cases", 0) for r in reports)
    all_cases = sum(r.get("total_cases", 1) for r in reports) or 1
    pass_rate = round((passed / all_cases) * 100, 1)

    with col1:
        st.metric("总报告数", total)
    with col2:
        st.metric("已完成", completed)
    with col3:
        st.metric("平均通过率", f"{pass_rate}%")

    st.divider()

    type_filter = st.selectbox("按类型筛选", ["全部", "api", "web"])
    filtered = reports if type_filter == "全部" else [r for r in reports if r.get("test_type") == type_filter]

    for report in filtered:
        color = "green" if report.get("status") == "completed" else "orange"
        with st.expander(f"📄 [{report.get('test_type','')}] {report.get('test_name', '')} - {report.get('status','')}"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.write(f"**状态**: :{color}[{report.get('status','')}]")
            with c2:
                st.write(f"**总用例**: {report.get('total_cases', 0)}")
            with c3:
                st.write(f"**通过**: {report.get('passed_cases', 0)}")
            with c4:
                st.write(f"**失败**: {report.get('failed_cases', 0)}")
            st.write(f"**时间**: {report.get('created_at','')[:19]}")

            if report.get("logs"):
                try:
                    logs = json.loads(report["logs"])
                    if logs:
                        st.markdown("**执行日志:**")
                        for log in logs:
                            icon = "✅" if log.get("status") == "passed" else "❌"
                            st.write(f"  {icon} {log.get('message', '')}")
                except:
                    pass


def render_user_management():
    st.title("👥 用户管理")

    st.info("📋 本页面展示所有注册用户及其会话信息。")

    try:
        users = fetch_data("admin/users")
        if not users:
            st.info("暂无用户。")
            return

        st.metric("总用户数", len(users))

        st.divider()

        for user in users:
            with st.expander(f"👤 {user['username']} (ID: {user['id']})"):
                st.write(f"**创建时间**: {user['created_at'][:19]}")

                sessions = fetch_data(f"admin/users/{user['id']}/sessions")
                if sessions:
                    st.subheader("会话列表")
                    for session in sessions:
                        st.write(f"- {session['name']} (ID: {session['session_id']}) - {session['created_at'][:19]}")
                else:
                    st.write("暂无会话")
    except Exception as e:
        st.error(f"加载失败: {e}")

# ============================================
# 路由分发
# ============================================
if not st.session_state.token:
    render_login()
else:
    render_sidebar()
    if st.session_state.current_page == "ai_assistant":
        render_ai_assistant()
    elif st.session_state.current_page == "knowledge_base":
        render_knowledge_base()
    elif st.session_state.current_page == "api_test":
        render_api_test()
    elif st.session_state.current_page == "web_automation":
        render_web_automation()
    elif st.session_state.current_page == "test_reports":
        render_test_reports()
    elif st.session_state.current_page == "user_management":
        render_user_management()