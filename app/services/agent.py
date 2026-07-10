# app/services/agent.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# 1. 定义状态（State）
# ============================================
class AgentState(TypedDict):
    messages: list           # 对话历史
    next_step: str           # 下一步要做什么

# ============================================
# 2. 创建模型
# ============================================
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0.3
)

# ============================================
# 3. 定义节点（Node）函数
# ============================================

# 节点1：意图识别
def identify_intent(state: AgentState):
    """判断用户想做什么"""
    user_message = state["messages"][-1]["content"]
    
    # 简单关键词匹配（后续会升级为 LLM 判断）
    if "测试用例" in user_message or "生成用例" in user_message:
        state["next_step"] = "generate_case"
    elif "接口测试" in user_message or "API测试" in user_message:
        state["next_step"] = "run_api_test"      # 新增
    elif "Web自动化" in user_message or "浏览器" in user_message:
        state["next_step"] = "run_web_test"      # 新增
    elif "运行" in user_message and "测试" in user_message:
        state["next_step"] = "run_test"
    else:
        state["next_step"] = "chat"
    
    return state

# 节点2：生成测试用例
def generate_case(state: AgentState):
    """生成测试用例"""
    state["messages"].append({
        "role": "assistant",
        "content": "📋 已生成登录测试用例：\n1. 打开登录页面\n2. 输入用户名\n3. 输入密码\n4. 点击登录按钮\n5. 验证登录成功"
    })
    state["next_step"] = "end"
    return state

# ============================================
# 节点：执行接口测试
# ============================================
def run_api_test(state: AgentState):
    """执行接口测试（目前为示例）"""
    state["messages"].append({
        "role": "assistant",
        "content": "🧪 正在执行接口测试：\n1. 测试GET /api/users → 200 OK\n2. 测试POST /api/login → 200 OK\n3. 测试GET /api/order → 401 Unauthorized\n\n✅ 接口测试完成，3个通过，0个失败"
    })
    state["next_step"] = "end"
    return state

# ============================================
# 节点：执行 Web 自动化测试
# ============================================
def run_web_test(state: AgentState):
    """执行 Web 自动化测试（目前为示例）"""
    state["messages"].append({
        "role": "assistant",
        "content": "🌐 正在执行 Web 自动化测试：\n1. 打开登录页面 → 成功\n2. 输入用户名 → 成功\n3. 输入密码 → 成功\n4. 点击登录按钮 → 成功\n5. 验证登录成功 → 通过\n\n✅ Web自动化测试完成，全部通过"
    })
    state["next_step"] = "end"
    return state

# 节点3：普通聊天
def chat(state: AgentState):
    """普通对话"""
    user_message = state["messages"][-1]["content"]
    response = llm.invoke(user_message)
    state["messages"].append({
        "role": "assistant",
        "content": response.content
    })
    state["next_step"] = "end"
    return state

# ============================================
# 4. 构建图（Graph）
# ============================================
def build_agent():
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("identify_intent", identify_intent)
    workflow.add_node("generate_case", generate_case)
    workflow.add_node("run_api_test", run_api_test)   # 新增
    workflow.add_node("run_web_test", run_web_test)   # 新增
    workflow.add_node("chat", chat)
    
    # 设置入口节点
    workflow.set_entry_point("identify_intent")
    
    # 添加条件边（根据意图决定下一步）
    workflow.add_conditional_edges(
        "identify_intent",
        lambda state: state["next_step"],
        {
            "generate_case": "generate_case",
            "run_api_test": "run_api_test",
            "run_web_test": "run_web_test",
            "chat": "chat",
            "end": END
        }
    )
    
    # 添加结束边
    workflow.add_edge("generate_case", END)
    workflow.add_edge("run_api_test", END)
    workflow.add_edge("run_web_test", END)
    workflow.add_edge("chat", END)
    
    # 编译
    return workflow.compile()

# ============================================
# 5. 对外接口
# ============================================
agent = build_agent()

def run_agent(user_message: str) -> str:
    """运行 Agent，返回最终回答"""
    initial_state = {
        "messages": [{"role": "user", "content": user_message}],
        "next_step": ""
    }
    result = agent.invoke(initial_state)
    # 返回最后一条 AI 消息
    for msg in reversed(result["messages"]):
        if msg["role"] == "assistant":
            return msg["content"]
    return "处理失败"