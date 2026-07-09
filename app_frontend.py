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
# 2. 初始化会话状态（记忆）
# ============================================
# Streamlit 每次用户操作都会重新运行整个脚本
# st.session_state 用来保存变量，让数据在多次运行间不丢失
if "session_id" not in st.session_state:
    st.session_state.session_id = None   # 当前选中的会话ID
if "messages" not in st.session_state:
    st.session_state.messages = []       # 当前会话的聊天历史
if "sessions" not in st.session_state:
    st.session_state.sessions = []       # 所有会话列表


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
        else:
            st.warning("⚠️ 请输入会话名称")
    
    st.divider()
    
    # 获取会话列表
    st.subheader("📂 已有会话")
    if st.button("刷新会话列表"):
        response = requests.get(f"{API_BASE}/sessions/")
        if response.status_code == 200:
            st.session_state.sessions = response.json()
            st.success(f"✅ 已加载 {len(st.session_state.sessions)} 个会话")
        else:
            st.error("❌ 加载失败")
    
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
# 主区域：聊天界面
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
        
        # TODO: 调用后端聊天接口（第4天最后一步）
        # 调用后端聊天接口
try:
    response = requests.post(
        f"{API_BASE}/chat/stream",
        json={
            "message": user_input,
            "session_id": st.session_state.session_id
        },
        stream=True
    )
    
    if response.status_code == 200:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        chunk = line[6:]
                        full_response += chunk
                        placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.error(f"❌ 请求失败：{response.status_code}")
except Exception as e:
    st.error(f"❌ 连接失败：{e}")