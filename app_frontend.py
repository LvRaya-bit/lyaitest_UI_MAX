import streamlit as st
import requests

# ============================================
# 1. 页面配置
# ============================================
st.set_page_config(
    page_title="LYAITEST AI测试平台",
    page_icon="🤖"
)
st.title("🤖 LYAITEST AI测试平台")

st.write("欢迎使用 LYAITEST！")

# ============================================
# 2. 初始化会话状态
# ============================================
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions" not in st.session_state:
    st.session_state.sessions = []

# ============================================
# 后端 API 地址
# ============================================
API_BASE = "http://localhost:8000/api/v1"

# ============================================
# 3. 侧边栏
# ============================================
with st.sidebar:
    st.header("📋 会话管理")
    
    # 创建会话
    st.subheader("🆕 创建新会话")
    session_name = st.text_input("会话名称", placeholder="输入会话名称...")
    if st.button("创建会话"):
        if session_name:
            try:
                response = requests.post(
                    f"{API_BASE}/sessions/",
                    json={"name": session_name}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.success(f"✅ 会话已创建：{data['session_id']}")
                else:
                    st.error("❌ 创建失败")
            except Exception as e:
                st.error(f"❌ 连接失败：{e}")
        else:
            st.warning("⚠️ 请输入会话名称")
    
    st.divider()
    
    # 获取会话列表
    st.subheader("📂 已有会话")
    if st.button("刷新会话列表"):
        try:
            response = requests.get(f"{API_BASE}/sessions/")
            if response.status_code == 200:
                st.session_state.sessions = response.json()
                st.success(f"✅ 已加载 {len(st.session_state.sessions)} 个会话")
            else:
                st.error("❌ 加载失败")
        except Exception as e:
            st.error(f"❌ 连接失败：{e}")
    
    # 显示会话列表
    for s in st.session_state.sessions:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"📌 {s['name']}", key=s["session_id"]):
                st.session_state.session_id = s["session_id"]
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{s['session_id']}"):
                try:
                    response = requests.delete(
                        f"{API_BASE}/sessions/{s['session_id']}"
                    )
                    if response.status_code == 200:
                        st.session_state.sessions = [
                            x for x in st.session_state.sessions 
                            if x["session_id"] != s["session_id"]
                        ]
                        if st.session_state.session_id == s["session_id"]:
                            st.session_state.session_id = None
                            st.session_state.messages = []
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ 删除失败：{e}")

# ============================================
# 4. 主区域：聊天界面
# ============================================
st.divider()

if st.session_state.session_id is None:
    st.info("👈 请先在左侧创建或选择一个会话")
else:
    st.success(f"当前会话：{st.session_state.session_id}")
    
    # 显示聊天历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # 输入框
    user_input = st.chat_input("输入消息...")
    if user_input:
        # 显示用户消息
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # 调用 Agent 接口
        try:
            response = requests.post(
                f"{API_BASE}/agent/",
                json={"message": user_input}
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data["reply"]
                
                with st.chat_message("assistant"):
                    st.write(reply)
                
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error(f"❌ 请求失败：{response.status_code}")
        except Exception as e:
            st.error(f"❌ 连接失败：{e}")