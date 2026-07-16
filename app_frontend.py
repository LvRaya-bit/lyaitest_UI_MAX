import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="LYAITEST AI测试平台", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

try:
    API_BASE = st.secrets.get("api_base", os.getenv("API_BASE", "http://localhost:8001/api/v1"))
except Exception:
    API_BASE = os.getenv("API_BASE", "http://localhost:8001/api/v1")


# ============================================================
# 全局样式：统一配色 #f8fafc 浅蓝底 / #3b82f6 天空蓝主按钮 / 白色圆角卡片
# ============================================================
def inject_global_css():
    st.markdown("""
    <style>
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        background-color: #f8fafc !important;
    }
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #f8fafc !important;
        color: #1e293b;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}

    /* 顶部 Header：消除白色条与缝隙 */
    [data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        visibility: hidden !important;
    }
    [data-testid="stHeader"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    header[data-testid="stHeader"]::before,
    header[data-testid="stHeader"]::after {
        display: none !important;
        content: none !important;
    }

    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 20px !important;
    }
    /* 侧边栏折叠后恢复按钮：确保可见可点击 */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        z-index: 9999 !important;
    }

    /* 主内容区 */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
        margin-top: 0 !important;
    }
    [data-testid="stAppViewContainer"] > section,
    section[data-testid="stMain"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stMainBlockContainer"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stHorizontalBlock"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        gap: 0 !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }
    /* 消除 Streamlit 默认的顶部间距容器 */
    [data-testid="stMain"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    /* 消除 stMarkdown 产生的空白块 */
    [data-testid="stMarkdown"] {
        margin-top: 0 !important;
    }
    /* 消除装饰性空 div */
    [data-testid="stDecoration"], [data-testid="stToolbar"] {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ===== 按钮统一样式：禁用红色/黑色 ===== */
    .stButton button, button[data-testid] {
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        transition: all 0.15s ease !important;
        white-space: nowrap !important;
    }
    .stButton button[kind="primary"] {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
    }
    .stButton button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
    }
    .stButton button[kind="secondary"]:hover {
        background-color: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
    }
    form [data-testid="stFormSubmitButton"] button {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
    }
    form [data-testid="stFormSubmitButton"] button:hover {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
    }

    /* ===== 输入框统一样式 ===== */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div, .stMultiSelect > div > div {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
    }

    /* ===== 卡片 ===== */
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 16px;
    }
    .card-title-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    .online-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: #10b981;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 999px;
        padding: 4px 10px;
    }
    .online-dot {
        width: 6px; height: 6px;
        background: #10b981; border-radius: 50%;
    }

    /* ===== 页面标题 ===== */
    .page-title {
        font-size: 24px;
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 4px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .page-subtitle {
        font-size: 14px;
        color: #64748b;
        margin: 0 0 20px 0;
    }

    /* ===== 提示横幅 ===== */
    .banner {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 12px 16px;
        color: #1e40af;
        font-size: 14px;
        margin-bottom: 20px;
    }

    .session-empty {
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        padding: 32px 0;
    }

    /* ===== AI 对话区 ===== */
    .ai-welcome {
        text-align: center;
        padding: 20px 12px 12px;
    }
    .ai-robot {
        width: 56px; height: 56px;
        background: #eff6ff; border-radius: 14px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 28px; margin-bottom: 12px;
    }
    .ai-hello { font-size: 20px; font-weight: 600; color: #1e293b; margin-bottom: 6px; }
    .ai-intro { font-size: 13px; color: #64748b; margin-bottom: 18px; }
    .quick-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 8px;
    }
    .quick-action {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 13px;
        color: #1e293b;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.15s;
    }
    .quick-action:hover { border-color: #3b82f6; background: #f8fafc; }
    .quick-action .arrow { color: #94a3b8; }

    .chat-tip { text-align: center; font-size: 12px; color: #94a3b8; margin-top: 8px; }

    .msg-row { display: flex; margin: 12px 0; }
    .msg-row.user { justify-content: flex-end; }
    .msg-row.assistant { justify-content: flex-start; }
    .msg-bubble {
        max-width: 80%;
        padding: 10px 14px;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    .msg-bubble.user { background: #3b82f6; color: #ffffff; }
    .msg-bubble.assistant { background: #f1f5f9; color: #1e293b; }

    /* ===== 顶部导航栏：加大内边距 ===== */
    .topnav-wrap {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 20px !important;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .topnav-wrap .stButton button {
        padding: 10px 18px !important;
        font-size: 14px !important;
        min-height: 40px !important;
    }
    .topnav-brand {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 17px;
        font-weight: 700;
        color: #1e293b;
        white-space: nowrap;
        padding: 10px 14px 10px 4px;
        border-right: 1px solid #e2e8f0;
    }
    .topnav-brand .logo-icon {
        width: 32px; height: 32px;
        background: #3b82f6; border-radius: 8px;
        display: inline-flex; align-items: center; justify-content: center;
        color: #fff; font-size: 17px;
    }

    /* ===== 侧边栏用户卡片 ===== */
    .sidebar-user-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin: 0 12px 16px;
    }
    .sidebar-user-avatar {
        width: 40px; height: 40px;
        background: #3b82f6; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        color: #fff; font-size: 18px; flex-shrink: 0;
    }
    .sidebar-user-name { font-size: 14px; font-weight: 600; color: #1e293b; }
    .sidebar-user-meta { font-size: 12px; color: #94a3b8; }
    .sidebar-section-title {
        font-size: 11px; font-weight: 600; color: #94a3b8;
        text-transform: uppercase; letter-spacing: 0.5px;
        padding: 0 16px 8px; margin-top: 8px;
    }

    /* ===== 统计卡片 ===== */
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
    }
    .stat-label { font-size: 12px; color: #64748b; }
    .stat-value { font-size: 24px; font-weight: 600; color: #1e293b; }

    .hide-me { display: none !important; }

    /* ===== 文档/列表项 ===== */
    .doc-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 8px;
        background: #ffffff;
    }
    .doc-item .doc-name { font-size: 14px; color: #1e293b; font-weight: 500; }
    .doc-item .doc-type { font-size: 12px; color: #94a3b8; }

    .editing-tag {
        display: inline-block;
        background: #eff6ff;
        color: #3b82f6;
        border: 1px solid #bfdbfe;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 12px;
        margin-left: 8px;
    }
    </style>
    """, unsafe_allow_html=True)


def clear_user_cache():
    keys_to_clear = ['sessions', 'messages', 'knowledge_bases', 'interfaces', 'web_cases',
                     'selected_session', 'selected_kb', 'selected_interface', 'selected_web_case',
                     'editing_interface', 'editing_web_case']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


# ============================================================
# 顶部全局导航栏：加大内边距、放大功能面板
# ============================================================
def render_top_navbar():
    nav_items = [
        ("AI助手中心", "🤖"),
        ("项目知识库", "📚"),
        ("接口测试", "🔌"),
        ("Web自动化", "🌐"),
        ("测试报告", "📊"),
        ("用户管理", "👥"),
    ]
    current = st.session_state.get("page", "AI助手中心")

    st.markdown('<div class="topnav-wrap">', unsafe_allow_html=True)

    cols = st.columns([1.4, 1, 1, 1, 1, 1, 1, 1])

    with cols[0]:
        st.markdown("""
        <div class="topnav-brand">
            <span class="logo-icon">🤖</span>
            <span>LYAITEST</span>
        </div>
        """, unsafe_allow_html=True)

    for i, (item, icon) in enumerate(nav_items):
        with cols[i + 1]:
            is_active = (current == item)
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{icon} {item}", key=f"nav_{item}", use_container_width=True, type=btn_type):
                st.session_state.page = item
                st.rerun()

    with cols[7]:
        if st.button("⏏ 退出", key="nav_logout", use_container_width=True, type="secondary"):
            clear_user_cache()
            for k in ["token", "username", "user_id"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# 侧边栏：仅展示用户信息（支持折叠后恢复展开）
# ============================================================
def render_sidebar():
    with st.sidebar:
        username = st.session_state.get("username", "用户")
        user_id = st.session_state.get("user_id", "-")
        st.markdown(f"""
        <div class="sidebar-user-card">
            <div class="sidebar-user-avatar">👤</div>
            <div>
                <div class="sidebar-user-name">{username}</div>
                <div class="sidebar-user-meta">ID: {user_id}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-title">账户信息</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="padding: 0 16px; font-size: 13px; color: #64748b; line-height: 2;">
            <div>👤 用户名：{username}</div>
            <div>🆔 用户ID：{user_id}</div>
            <div>🟢 状态：在线</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# 登录页：左右分栏垂直居中 + 消除底部留白 + 自适应窗口高度
# ============================================================
def render_login():
    inject_global_css()

    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none !important;}
    /* 登录页：彻底消除顶部白色缝隙 */
    [data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        background: transparent !important;
    }
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    /* 登录页主容器：占满视口高度 */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
        margin-top: 0 !important;
    }
    [data-testid="stAppViewContainer"] > section,
    section[data-testid="stMain"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stMainBlockContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stMain"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    /* 左右分栏容器：占满视口高度并垂直居中 */
    [data-testid="stHorizontalBlock"] {
        min-height: 100vh !important;
        align-items: stretch !important;
        gap: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        border: none !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    [data-testid="stHorizontalBlock"] > div > div {
        gap: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    [data-testid="stHorizontalBlock"] > div:first-child {
        min-height: 100vh !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
    }
    /* 左侧品牌面板 */
    .login-left {
        min-height: 100vh;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: #ffffff;
        padding: 60px 56px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .login-left .logo-circle {
        width: 64px; height: 64px;
        background: rgba(255,255,255,0.2);
        border-radius: 16px;
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; margin-bottom: 24px;
    }
    .login-left h1 { font-size: 34px; font-weight: 700; margin: 0 0 12px; }
    .login-left .sub { font-size: 15px; opacity: 0.9; margin-bottom: 32px; line-height: 1.6; }
    .login-left .feature { display: flex; align-items: center; gap: 10px; font-size: 14px; opacity: 0.95; margin-bottom: 14px; }
    .login-left .feature .dot { width: 6px; height: 6px; background: #ffffff; border-radius: 50%; opacity: 0.7; }
    /* 右侧表单面板：标准分栏，无独立卡片容器 */
    .login-right-wrap {
        background: transparent;
        padding: 0;
        margin: 0;
    }
    .login-right-wrap .welcome { font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
    .login-right-wrap .tip { font-size: 14px; color: #64748b; margin-bottom: 28px; }
    /* 右列容器：浅蓝底色，占满视口高度 */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        background: #f8fafc;
        min-height: 100vh;
        padding: 0 !important;
    }
    /* 右列内容：内部统一内边距，作为整体垂直居中 */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) > div {
        padding-left: 56px !important;
        padding-right: 56px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }
    .login-footer { text-align: center; font-size: 12px; color: #94a3b8; margin-top: 24px; }
    /* Tabs 样式 */
    .stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid #e2e8f0; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
        padding: 10px 24px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        border-bottom: 2px solid transparent !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"][data-baseweb="tab"] {
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #3b82f6 !important; }
    .stTabs [data-baseweb="tab-border"] { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([38, 62], gap="small")

    with col_left:
        st.markdown("""
        <div class="login-left">
            <div class="logo-circle">🤖</div>
            <h1>LYAITEST</h1>
            <div class="sub">AI 驱动的测试智能体平台<br/>让测试资产的创建、维护与执行更高效</div>
            <div class="feature"><span class="dot"></span> AI 对话式测试用例生成</div>
            <div class="feature"><span class="dot"></span> 项目知识库智能检索</div>
            <div class="feature"><span class="dot"></span> 接口与 Web 自动化素材管理</div>
            <div class="feature"><span class="dot"></span> 测试报告自动归档</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="login-right-wrap">
            <div class="welcome">欢迎使用 👋</div>
            <div class="tip">登录或注册以开始使用 LYAITEST 平台</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["登录", "注册"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("用户名", placeholder="请输入用户名")
                password = st.text_input("密码", type="password", placeholder="请输入密码")
                submitted = st.form_submit_button("登 录", use_container_width=True, type="primary")
            if submitted:
                if not username or not password:
                    st.error("请输入用户名和密码")
                else:
                    try:
                        r = requests.post(f"{API_BASE}/auth/login", data={"username": username, "password": password})
                        if r.status_code == 200:
                            result = r.json()
                            clear_user_cache()
                            st.session_state.token = result["access_token"]
                            st.session_state.username = result["username"]
                            st.session_state.user_id = result["user_id"]
                            st.success("登录成功")
                            st.rerun()
                        else:
                            st.error("用户名或密码错误")
                    except Exception as e:
                        st.error(f"登录失败: {str(e)}")

        with tab_register:
            with st.form("register_form", clear_on_submit=False):
                r_username = st.text_input("用户名", placeholder="请输入用户名")
                r_password = st.text_input("密码", type="password", placeholder="请输入密码")
                r_confirm = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
                r_submitted = st.form_submit_button("注 册", use_container_width=True, type="primary")
            if r_submitted:
                if not r_username or not r_password:
                    st.error("请输入用户名和密码")
                elif r_password != r_confirm:
                    st.error("两次密码输入不一致")
                else:
                    try:
                        r = requests.post(f"{API_BASE}/auth/register", json={"username": r_username, "password": r_password})
                        if r.status_code == 200:
                            st.success("注册成功，请切换到登录 Tab 登录")
                        else:
                            try:
                                st.error(r.json().get("detail", "注册失败"))
                            except Exception:
                                st.error("注册失败")
                    except Exception as e:
                        st.error(f"注册失败: {str(e)}")

        st.markdown('<div class="login-footer">登录即表示你同意平台使用条款与隐私政策</div>', unsafe_allow_html=True)


# ============================================================
# API 辅助函数
# ============================================================
def get_headers():
    if "token" in st.session_state:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def fetch_data(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=get_headers())
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            st.session_state.clear()
            st.rerun()
        return []
    except Exception:
        return []


def call_api(method, endpoint, **kwargs):
    try:
        r = requests.request(method, f"{API_BASE}{endpoint}", headers=get_headers(), **kwargs)
        if r.status_code == 401:
            st.session_state.clear()
            st.rerun()
        return r
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None


# ============================================================
# AI 助手中心：左右等宽卡片
# - 支持自定义会话名称 + 删除会话
# - 支持选择知识库/接口/Web用例执行测试
# ============================================================
def render_ai_assistant():
    st.markdown("""
    <h1 class="page-title"><span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:#eff6ff;border-radius:8px;font-size:18px;">🤖</span> AI 助手中心</h1>
    <p class="page-subtitle">与小测协作，快速完成测试资产维护与执行</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([22, 78], gap="medium")

    # ---- 左侧：会话管理（新建自定义名称 + 删除 + 绑定知识库） ----
    with col1:
        st.markdown('<div class="card"><div class="card-title">💬 会话管理</div>', unsafe_allow_html=True)

        with st.form("new_session_form", clear_on_submit=True):
            new_name = st.text_input("会话名称", placeholder="输入会话名称（留空则自动生成）")
            submitted = st.form_submit_button("✨ 新建对话", use_container_width=True, type="primary")
        if submitted:
            payload_name = new_name.strip() if new_name.strip() else "新对话"
            r = call_api("POST", "/sessions/", json={"name": payload_name})
            if r and r.status_code == 200:
                st.session_state.selected_session = r.json()["session_id"]
                st.session_state.messages = []
                st.success(f"会话「{payload_name}」已创建")
                st.rerun()

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # 预加载知识库列表，供会话绑定使用
        kb_list = fetch_data("/knowledge-base/")

        sessions = fetch_data("/sessions/")
        if sessions:
            for s in sessions:
                sid = s["session_id"]
                is_selected = st.session_state.get("selected_session") == sid
                s_col1, s_col2 = st.columns([4, 1])
                with s_col1:
                    btn_type = "primary" if is_selected else "secondary"
                    if st.button(f"💬 {s['name']}", key=f"session_{sid}", use_container_width=True, type=btn_type):
                        st.session_state.selected_session = sid
                        msgs = fetch_data(f"/sessions/{sid}/messages")
                        st.session_state.messages = msgs if msgs else []
                        st.rerun()
                with s_col2:
                    if st.button("🗑", key=f"del_session_{sid}", use_container_width=True, type="secondary", help="删除会话"):
                        r = call_api("DELETE", f"/sessions/{sid}")
                        if r and r.status_code == 200:
                            if st.session_state.get("selected_session") == sid:
                                st.session_state.selected_session = None
                                st.session_state.messages = []
                            st.success("已删除")
                            st.rerun()

                # 选中会话显示知识库绑定切换器
                if is_selected:
                    current_kb_id = s.get("knowledge_base_id")
                    kb_options = ["未绑定"] + [f"{kb['name']} ({kb['id']})" for kb in kb_list]
                    # 计算当前选中项索引
                    default_idx = 0
                    if current_kb_id:
                        for i, kb in enumerate(kb_list):
                            if kb["id"] == current_kb_id:
                                default_idx = i + 1
                                break
                    bind_kb = st.selectbox(
                        "📚 绑定知识库",
                        kb_options,
                        index=default_idx,
                        key=f"bind_kb_{sid}",
                        help="切换后点击保存即更新当前会话绑定的知识库"
                    )
                    if st.button("💾 保存知识库绑定", key=f"save_kb_{sid}", use_container_width=True, type="secondary"):
                        new_kb_id = None if bind_kb == "未绑定" else bind_kb.split("(")[-1].replace(")", "").strip()
                        r = call_api("PUT", f"/sessions/{sid}", json={"knowledge_base_id": new_kb_id})
                        if r and r.status_code == 200:
                            st.success("知识库绑定已更新")
                            st.rerun()
                        else:
                            st.error("绑定失败")
        else:
            st.markdown('<div class="session-empty">暂无历史会话<br/>上方输入名称新建对话</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- 右侧：AI 对话卡片 ----
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title-row">
                <span class="card-title">
                    <span style="display:inline-block;width:8px;height:8px;background:#3b82f6;border-radius:50%;margin-right:8px;"></span>
                    🤖 小测 · AI 测试助手
                </span>
                <span class="online-badge"><span class="online-dot"></span>在线</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        selected_session = st.session_state.get("selected_session")

        # 机器人欢迎区 + 快捷指令
        st.markdown("""
        <div class="ai-welcome">
            <div class="ai-robot">🤖</div>
            <div class="ai-hello">你好，我是小测</div>
            <div class="ai-intro">查数据、跑测试、生成用例、记录结果，测试工作都可以直接交给我。</div>
            <div class="quick-grid">
                <div class="quick-action"><span>📊 查看项目整体情况</span><span class="arrow">›</span></div>
                <div class="quick-action"><span>📈 最近 7 天测试执行</span><span class="arrow">›</span></div>
                <div class="quick-action"><span>📝 生成测试用例</span><span class="arrow">›</span></div>
                <div class="quick-action"><span>🔍 查询测试报告</span><span class="arrow">›</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 消息列表
        if "messages" in st.session_state and st.session_state.messages:
            for msg in st.session_state.messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                st.markdown(f"""
                <div class="msg-row {role}">
                    <div class="msg-bubble {role}">{content}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="chat-tip">AI 可能会出错，请核对关键测试结果</div>', unsafe_allow_html=True)

        # 执行目标选择器：接口 / Web用例（知识库已在左侧会话管理中绑定）
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        with st.expander("🎯 选择执行目标（可选，用于直接执行指定素材）", expanded=False):
            interfaces = fetch_data("/api-test/interfaces")
            web_cases = fetch_data("/web-automation/cases")

            if_options = ["不选择"] + [f"{itf['name']} [{itf.get('method','GET')}] ({itf['id']})" for itf in interfaces]
            web_options = ["不选择"] + [f"{c['name']} ({c['id']})" for c in web_cases]

            sel_if = st.selectbox("🔌 执行接口", if_options, key="agent_sel_if")
            sel_web = st.selectbox("🌐 执行Web用例", web_options, key="agent_sel_web")

            # 直接执行按钮：每个按钮只传对应 ID，避免类型错乱
            def _extract_id(sel_str):
                if not sel_str or sel_str.startswith("不"):
                    return None
                return sel_str.split("(")[-1].replace(")", "").strip()

            exec_col1, exec_col2 = st.columns(2)
            with exec_col1:
                run_if_btn = st.button("▶ 执行接口测试", key="run_if_direct", use_container_width=True, type="primary",
                                       disabled=(sel_if == "不选择"))
            with exec_col2:
                run_web_btn = st.button("▶ 执行Web测试", key="run_web_direct", use_container_width=True, type="primary",
                                        disabled=(sel_web == "不选择"))

            # 直接执行接口测试
            if run_if_btn and sel_if != "不选择":
                if not selected_session:
                    st.warning("请先在左侧新建或选择一个会话")
                else:
                    if "messages" not in st.session_state:
                        st.session_state.messages = []
                    if_id = _extract_id(sel_if)
                    st.session_state.messages.append({"role": "user", "content": f"▶ 直接执行接口测试: {sel_if}"})
                    with st.spinner("正在执行接口测试..."):
                        r = call_api("POST", "/agent/", json={
                            "message": "执行选中的接口测试",
                            "session_id": selected_session,
                            "interface_id": if_id,
                            "web_case_id": None,
                        })
                        if r and r.status_code == 200:
                            response = r.json().get("reply", r.json().get("response", ""))
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        else:
                            err_msg = "接口测试执行失败"
                            if r is not None:
                                try:
                                    err_msg = r.json().get("detail", err_msg)
                                except Exception:
                                    err_msg = r.text[:200]
                            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {err_msg}"})
                    st.rerun()

            # 直接执行 Web 测试
            if run_web_btn and sel_web != "不选择":
                if not selected_session:
                    st.warning("请先在左侧新建或选择一个会话")
                else:
                    if "messages" not in st.session_state:
                        st.session_state.messages = []
                    web_id = _extract_id(sel_web)
                    st.session_state.messages.append({"role": "user", "content": f"▶ 直接执行Web测试: {sel_web}"})
                    with st.spinner("正在执行Web测试..."):
                        r = call_api("POST", "/agent/", json={
                            "message": "执行选中的Web自动化测试",
                            "session_id": selected_session,
                            "interface_id": None,
                            "web_case_id": web_id,
                        })
                        if r and r.status_code == 200:
                            response = r.json().get("reply", r.json().get("response", ""))
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        else:
                            err_msg = "Web测试执行失败"
                            if r is not None:
                                try:
                                    err_msg = r.json().get("detail", err_msg)
                                except Exception:
                                    err_msg = r.text[:200]
                            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {err_msg}"})
                    st.rerun()

        # 底部输入框 + 发送按钮（普通对话，不绑定接口/Web ID，由 agent 按意图自动判断）
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        input_col, btn_col = st.columns([4, 1])
        with input_col:
            user_input = st.text_input("消息", label_visibility="collapsed", placeholder="输入测试需求…", key="ai_input")
        with btn_col:
            send_clicked = st.button("发送 ➤", key="ai_send", use_container_width=True, type="primary")

        if send_clicked and user_input:
            if not selected_session:
                st.warning("请先在左侧新建或选择一个会话")
            else:
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append({"role": "user", "content": user_input})

                with st.spinner("小测思考中..."):
                    # 普通对话不传 interface_id / web_case_id，由 agent 按自然语言意图自动判断
                    r = call_api("POST", "/agent/", json={
                        "message": user_input,
                        "session_id": selected_session,
                    })
                    if r and r.status_code == 200:
                        try:
                            response = r.json().get("reply", r.json().get("response", ""))
                        except Exception:
                            response = ""
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        err_msg = "AI 处理失败"
                        if r is not None:
                            try:
                                err_msg = r.json().get("detail", err_msg)
                            except Exception:
                                err_msg = r.text[:200]
                        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {err_msg}"})
                st.rerun()


# ============================================================
# 项目知识库：左侧知识库管理 + 右侧文档管理
# ============================================================
def render_knowledge_base():
    st.markdown("""
    <h1 class="page-title"><span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:#eff6ff;border-radius:8px;font-size:18px;">📚</span> 项目知识库</h1>
    <p class="page-subtitle">上传项目文档，构建团队共享的 AI 知识库</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📁 知识库管理</div>', unsafe_allow_html=True)
        with st.form("create_kb_form", clear_on_submit=True):
            kb_name = st.text_input("知识库名称", placeholder="请输入知识库名称")
            kb_description = st.text_area("描述", placeholder="简要描述知识库用途")
            if st.form_submit_button("创建知识库", use_container_width=True, type="primary"):
                if kb_name:
                    r = call_api("POST", "/knowledge-base/", data={"name": kb_name, "description": kb_description})
                    if r and r.status_code == 200:
                        st.success("创建成功")
                        st.rerun()
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if st.button("🔄 刷新列表", key="refresh_kb", use_container_width=True, type="secondary"):
            st.rerun()

        knowledge_bases = fetch_data("/knowledge-base/")
        if knowledge_bases:
            for kb in knowledge_bases:
                is_selected = st.session_state.get("selected_kb") == kb["id"]
                btn_type = "primary" if is_selected else "secondary"
                if st.button(f"📚 {kb['name']}", key=f"kb_{kb['id']}", use_container_width=True, type=btn_type):
                    st.session_state.selected_kb = kb["id"]
                    st.rerun()
        else:
            st.markdown('<div class="session-empty">暂无知识库</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        selected_kb = st.session_state.get("selected_kb")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if selected_kb:
            kb_info = fetch_data(f"/knowledge-base/{selected_kb}")
            kb_name = kb_info.get("name", "知识库") if kb_info else "知识库"
            st.markdown(f'<div class="card-title">📄 {kb_name} · 文档管理</div>', unsafe_allow_html=True)

            uploaded_file = st.file_uploader("上传文档", type=["txt", "md", "markdown", "pdf", "docx", "json"], key="kb_upload")
            if uploaded_file is not None:
                if st.button("📤 上传文档", key="upload_doc", use_container_width=True, type="primary"):
                    r = call_api("POST", f"/knowledge-base/{selected_kb}/documents",
                                 files={"file": (uploaded_file.name, uploaded_file.getvalue())})
                    if r and r.status_code == 200:
                        st.success(f"文档 {uploaded_file.name} 上传成功")
                        st.rerun()

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            documents = fetch_data(f"/knowledge-base/{selected_kb}/documents")
            if documents:
                for doc in documents:
                    st.markdown(f"""
                    <div class="doc-item">
                        <div>
                            <div class="doc-name">{doc.get('filename', '未命名')}</div>
                            <div class="doc-type">类型: {doc.get('file_type', '-')} · {doc.get('created_at', '')[:10]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    d_col1, d_col2 = st.columns([1, 1])
                    with d_col1:
                        if st.button("⬇ 下载", key=f"dl_{doc['id']}", use_container_width=True, type="secondary"):
                            r = call_api("GET", f"/knowledge-base/{selected_kb}/documents/{doc['id']}/download")
                            if r and r.status_code == 200:
                                st.download_button("保存文件", data=r.content, file_name=doc.get("filename", "doc"), key=f"save_{doc['id']}")
                    with d_col2:
                        if st.button("🗑 删除", key=f"del_{doc['id']}", use_container_width=True, type="secondary"):
                            r = call_api("DELETE", f"/knowledge-base/{selected_kb}/documents/{doc['id']}")
                            if r and r.status_code == 200:
                                st.success("删除成功")
                                st.rerun()
            else:
                st.markdown('<div class="session-empty">暂无文档，请上传</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card-title">📄 文档管理</div>', unsafe_allow_html=True)
            st.markdown('<div class="session-empty">请在左侧选择一个知识库<br/>或新建知识库后上传文档</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# 接口测试：仅素材管理 + 列表点击回填表单查看编辑
# ============================================================
def render_api_test():
    # pending-load：在表单 widget 渲染前设置值，避免 "widget already rendered" 错误
    if st.session_state.pop("_pending_load_interface", None):
        detail = st.session_state.get("editing_interface", {})
        st.session_state.if_name = detail.get("name", "")
        st.session_state.if_url = detail.get("url", "")
        st.session_state.if_method = detail.get("method", "GET")
        st.session_state.if_headers = json.dumps(detail.get("headers", {}), ensure_ascii=False, indent=2)
        st.session_state.if_params = json.dumps(detail.get("params", {}), ensure_ascii=False, indent=2)
        st.session_state.if_body = json.dumps(detail.get("body", {}), ensure_ascii=False, indent=2)

    st.markdown("""
    <h1 class="page-title"><span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:#eff6ff;border-radius:8px;font-size:18px;">🔌</span> 接口测试</h1>
    <p class="page-subtitle">维护接口测试素材，点击列表条目可查看与编辑</p>
    """, unsafe_allow_html=True)
    st.markdown('<div class="banner">📌 本页面仅用于维护测试素材（接口定义），不提供执行入口。执行任务请前往【AI 助手中心】发起。</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="medium")

    editing = st.session_state.get("editing_interface")  # dict or None

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if editing:
            st.markdown(f'<div class="card-title">✏️ 编辑接口<span class="editing-tag">编辑中：{editing.get("name","")}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card-title">➕ 新建接口</div>', unsafe_allow_html=True)

        with st.form("interface_form", clear_on_submit=False):
            if_name = st.text_input("接口名称", key="if_name", placeholder="请输入接口名称")
            if_url = st.text_input("请求 URL", key="if_url", placeholder="https://api.example.com/endpoint")
            if_method = st.selectbox("请求方法", ["GET", "POST", "PUT", "DELETE"], key="if_method")
            if_headers = st.text_area("Headers (JSON)", key="if_headers", height=80)
            if_params = st.text_area("Params (JSON)", key="if_params", height=80)
            if_body = st.text_area("Body (JSON)", key="if_body", height=80)

            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                save_new = st.form_submit_button("💾 新建保存", use_container_width=True, type="primary")
            with f_col2:
                update_btn = st.form_submit_button("🔄 更新", use_container_width=True, type="secondary", disabled=(not editing))
            with f_col3:
                cancel_btn = st.form_submit_button("✖ 取消编辑", use_container_width=True, type="secondary")

        if save_new:
            if if_name and if_url:
                try:
                    headers_json = json.loads(if_headers) if if_headers else {}
                    params_json = json.loads(if_params) if if_params else {}
                    body_json = json.loads(if_body) if if_body else {}
                    r = call_api("POST", "/api-test/interfaces", json={
                        "name": if_name, "url": if_url, "method": if_method,
                        "headers": headers_json, "params": params_json, "body": body_json,
                    })
                    if r and r.status_code == 200:
                        st.success("保存成功")
                        _reset_interface_form()
                        st.rerun()
                except json.JSONDecodeError:
                    st.error("JSON 格式错误，请检查 Headers / Params / Body")
            else:
                st.error("请填写接口名称和 URL")

        if update_btn and editing:
            if_id_val = editing.get("id")
            try:
                headers_json = json.loads(if_headers) if if_headers else {}
                params_json = json.loads(if_params) if if_params else {}
                body_json = json.loads(if_body) if if_body else {}
                r = call_api("PUT", f"/api-test/interfaces/{if_id_val}", json={
                    "name": if_name, "url": if_url, "method": if_method,
                    "headers": headers_json, "params": params_json, "body": body_json,
                })
                if r and r.status_code == 200:
                    st.success("更新成功")
                    _reset_interface_form()
                    st.rerun()
            except json.JSONDecodeError:
                st.error("JSON 格式错误，请检查 Headers / Params / Body")

        if cancel_btn:
            _reset_interface_form()
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 接口列表（点击查看编辑）</div>', unsafe_allow_html=True)
        if st.button("🔄 刷新列表", key="refresh_interfaces", use_container_width=True, type="secondary"):
            st.rerun()
        interfaces = fetch_data("/api-test/interfaces")
        if interfaces:
            for interface in interfaces:
                is_selected = st.session_state.get("selected_interface") == interface["id"]
                btn_type = "primary" if is_selected else "secondary"
                label = f"{interface.get('method','GET')}  {interface['name']}"
                row_c1, row_c2 = st.columns([4, 1])
                with row_c1:
                    if st.button(label, key=f"interface_{interface['id']}", use_container_width=True, type=btn_type):
                        detail = fetch_data(f"/api-test/interfaces/{interface['id']}")
                        if detail:
                            st.session_state.editing_interface = detail
                            st.session_state.selected_interface = interface["id"]
                            st.session_state._pending_load_interface = True
                            st.rerun()
                with row_c2:
                    if st.button("🗑", key=f"del_if_{interface['id']}", use_container_width=True, type="secondary", help="删除"):
                        r = call_api("DELETE", f"/api-test/interfaces/{interface['id']}")
                        if r and r.status_code == 200:
                            if st.session_state.get("selected_interface") == interface["id"]:
                                _reset_interface_form()
                            st.success("已删除")
                            st.rerun()
        else:
            st.markdown('<div class="session-empty">暂无接口<br/>请在左侧新建</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def _reset_interface_form():
    """清空接口表单的 session_state"""
    st.session_state.editing_interface = None
    st.session_state.selected_interface = None
    for k in ["if_name", "if_url", "if_method", "if_headers", "if_params", "if_body"]:
        if k in st.session_state:
            del st.session_state[k]


def _load_interface_to_form(if_id):
    """拉取接口详情并回填表单"""
    detail = fetch_data(f"/api-test/interfaces/{if_id}")
    if detail:
        st.session_state.editing_interface = detail
        st.session_state.selected_interface = if_id
        st.session_state.if_name = detail.get("name", "")
        st.session_state.if_url = detail.get("url", "")
        st.session_state.if_method = detail.get("method", "GET")
        st.session_state.if_headers = json.dumps(detail.get("headers", {}), ensure_ascii=False, indent=2)
        st.session_state.if_params = json.dumps(detail.get("params", {}), ensure_ascii=False, indent=2)
        st.session_state.if_body = json.dumps(detail.get("body", {}), ensure_ascii=False, indent=2)
        st.rerun()


# ============================================================
# Web 自动化：仅素材管理 + 列表点击回填表单查看编辑
# ============================================================
def render_web_automation():
    # pending-load：在表单 widget 渲染前设置值，避免 "widget already rendered" 错误
    if st.session_state.pop("_pending_load_web_case", None):
        detail = st.session_state.get("editing_web_case", {})
        st.session_state.wc_name = detail.get("name", "")
        st.session_state.wc_desc = detail.get("description", "")
        st.session_state.wc_steps = json.dumps(detail.get("steps", []), ensure_ascii=False, indent=2)

    st.markdown("""
    <h1 class="page-title"><span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:#eff6ff;border-radius:8px;font-size:18px;">🌐</span> Web 自动化</h1>
    <p class="page-subtitle">维护 Web 自动化用例，点击列表条目可查看与编辑</p>
    """, unsafe_allow_html=True)
    st.markdown('<div class="banner">📌 本页面仅用于维护测试素材（用例），不提供执行入口。执行任务请前往【AI 助手中心】发起。</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="medium")

    editing = st.session_state.get("editing_web_case")

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if editing:
            st.markdown(f'<div class="card-title">✏️ 编辑用例<span class="editing-tag">编辑中：{editing.get("name","")}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card-title">➕ 新建用例</div>', unsafe_allow_html=True)
        with st.form("web_case_form", clear_on_submit=False):
            wc_name = st.text_input("用例名称", key="wc_name", placeholder="请输入用例名称")
            wc_desc = st.text_area("用例描述", key="wc_desc", placeholder="简要描述用例场景")
            wc_steps = st.text_area("步骤 (JSON 数组)", key="wc_steps", height=100,
                                    placeholder='[{"action":"navigate","element":"url","value":"https://..."}]')

            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                save_new = st.form_submit_button("💾 新建保存", use_container_width=True, type="primary")
            with f_col2:
                update_btn = st.form_submit_button("🔄 更新", use_container_width=True, type="secondary", disabled=(not editing))
            with f_col3:
                cancel_btn = st.form_submit_button("✖ 取消编辑", use_container_width=True, type="secondary")

        if save_new:
            if wc_name:
                steps_list = []
                if wc_steps and wc_steps.strip():
                    try:
                        steps_list = json.loads(wc_steps)
                    except json.JSONDecodeError:
                        st.error("步骤 JSON 格式错误")
                        st.stop()
                r = call_api("POST", "/web-automation/cases", json={
                    "name": wc_name, "description": wc_desc, "steps": steps_list,
                })
                if r and r.status_code == 200:
                    st.success("保存成功")
                    _reset_web_case_form()
                    st.rerun()
            else:
                st.error("请填写用例名称")

        if update_btn and editing:
            case_id = editing.get("id")
            steps_list = []
            if wc_steps and wc_steps.strip():
                try:
                    steps_list = json.loads(wc_steps)
                except json.JSONDecodeError:
                    st.error("步骤 JSON 格式错误")
                    st.stop()
            r = call_api("PUT", f"/web-automation/cases/{case_id}", json={
                "name": wc_name, "description": wc_desc, "steps": steps_list,
            })
            if r and r.status_code == 200:
                st.success("更新成功")
                _reset_web_case_form()
                st.rerun()

        if cancel_btn:
            _reset_web_case_form()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 用例列表（点击查看编辑）</div>', unsafe_allow_html=True)
        if st.button("🔄 刷新列表", key="refresh_web_cases", use_container_width=True, type="secondary"):
            st.rerun()
        web_cases = fetch_data("/web-automation/cases")
        if web_cases:
            for case in web_cases:
                is_selected = st.session_state.get("selected_web_case") == case["id"]
                btn_type = "primary" if is_selected else "secondary"
                row_c1, row_c2 = st.columns([4, 1])
                with row_c1:
                    if st.button(f"🌐 {case['name']}", key=f"web_case_{case['id']}", use_container_width=True, type=btn_type):
                        detail = fetch_data(f"/web-automation/cases/{case['id']}")
                        if detail:
                            st.session_state.editing_web_case = detail
                            st.session_state.selected_web_case = case["id"]
                            st.session_state._pending_load_web_case = True
                            st.rerun()
                with row_c2:
                    if st.button("🗑", key=f"del_wc_{case['id']}", use_container_width=True, type="secondary", help="删除"):
                        r = call_api("DELETE", f"/web-automation/cases/{case['id']}")
                        if r and r.status_code == 200:
                            if st.session_state.get("selected_web_case") == case["id"]:
                                _reset_web_case_form()
                            st.success("已删除")
                            st.rerun()
        else:
            st.markdown('<div class="session-empty">暂无用例<br/>请在左侧新建</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def _reset_web_case_form():
    st.session_state.editing_web_case = None
    st.session_state.selected_web_case = None
    for k in ["wc_name", "wc_desc", "wc_steps"]:
        if k in st.session_state:
            del st.session_state[k]


def _load_web_case_to_form(case_id):
    detail = fetch_data(f"/web-automation/cases/{case_id}")
    if detail:
        st.session_state.editing_web_case = detail
        st.session_state.selected_web_case = case_id
        st.session_state.wc_name = detail.get("name", "")
        st.session_state.wc_desc = detail.get("description", "")
        st.session_state.wc_steps = json.dumps(detail.get("steps", []), ensure_ascii=False, indent=2)
        st.rerun()


# ============================================================
# 测试报告
# ============================================================
def render_report():
    st.markdown("""
    <h1 class="page-title"><span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:#eff6ff;border-radius:8px;font-size:18px;">📊</span> 测试报告</h1>
    <p class="page-subtitle">查看 AI 对话触发执行产生的运行记录</p>
    """, unsafe_allow_html=True)
    st.markdown('<div class="banner">📌 本页面展示 AI 对话触发执行产生的运行记录</div>', unsafe_allow_html=True)

    reports = fetch_data("/reports/")
    if reports:
        stat_cols = st.columns(3)
        total = len(reports)
        success = sum(1 for r in reports if r.get("status") == "completed")
        with stat_cols[0]:
            st.markdown(f'<div class="stat-card"><div class="stat-label">报告总数</div><div class="stat-value">{total}</div></div>', unsafe_allow_html=True)
        with stat_cols[1]:
            st.markdown(f'<div class="stat-card"><div class="stat-label">已完成</div><div class="stat-value" style="color:#10b981;">{success}</div></div>', unsafe_allow_html=True)
        with stat_cols[2]:
            st.markdown(f'<div class="stat-card"><div class="stat-label">运行中</div><div class="stat-value" style="color:#f59e0b;">{total - success}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        for report in reports:
            with st.expander(f"📄 {report.get('test_name') or report.get('title','未命名报告')}  —  {report.get('created_at', '')[:16]}"):
                st.markdown(f"<p><strong>状态：</strong> {report.get('status', '-')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><strong>类型：</strong> {report.get('test_type', '-')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><strong>通过/总数：</strong> {report.get('passed_cases',0)} / {report.get('total_cases',0)}</p>", unsafe_allow_html=True)
                if report.get("logs"):
                    try:
                        logs = json.loads(report["logs"]) if isinstance(report["logs"], str) else report["logs"]
                        st.json(logs)
                    except Exception:
                        st.text(report["logs"])
    else:
        st.markdown('<div class="card"><div class="session-empty" style="padding:60px 0;">暂无测试报告<br/>在【AI 助手中心】执行用例后会自动生成报告</div></div>', unsafe_allow_html=True)


# ============================================================
# 用户管理
# ============================================================
def render_user_management():
    st.markdown("""
    <h1 class="page-title"><span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:#eff6ff;border-radius:8px;font-size:18px;">👥</span> 用户管理</h1>
    <p class="page-subtitle">查看所有注册用户及其会话信息</p>
    """, unsafe_allow_html=True)
    st.markdown('<div class="banner">📌 本页面展示所有注册用户及其会话信息</div>', unsafe_allow_html=True)

    users = fetch_data("/admin/users")
    if users:
        st.markdown(f'<div class="stat-card"><div class="stat-label">总用户数</div><div class="stat-value">{len(users)}</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        for user in users:
            with st.expander(f"👤 {user.get('username', '')}  (ID: {user.get('id', '')})"):
                st.markdown(f"<p><strong>创建时间：</strong> {user.get('created_at', '-')}</p>", unsafe_allow_html=True)
                sessions = fetch_data(f"/admin/users/{user['id']}/sessions")
                if sessions:
                    st.markdown("<h4 style='margin-top:12px;color:#1e293b;'>会话列表：</h4>", unsafe_allow_html=True)
                    for session in sessions:
                        st.markdown(f"- 💬 {session.get('name', '')}  ({session.get('created_at', '')[:16]})")
                else:
                    st.markdown('<p style="color:#94a3b8;">暂无会话</p>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card"><div class="session-empty" style="padding:60px 0;">暂无用户</div></div>', unsafe_allow_html=True)


# ============================================================
# 主入口
# ============================================================
def main():
    if "token" not in st.session_state:
        render_login()
        return

    inject_global_css()
    render_top_navbar()
    render_sidebar()

    if "page" not in st.session_state:
        st.session_state.page = "AI助手中心"

    page = st.session_state.page
    if page == "AI助手中心":
        render_ai_assistant()
    elif page == "项目知识库":
        render_knowledge_base()
    elif page == "接口测试":
        render_api_test()
    elif page == "Web自动化":
        render_web_automation()
    elif page == "测试报告":
        render_report()
    elif page == "用户管理":
        render_user_management()


if __name__ == "__main__":
    main()
