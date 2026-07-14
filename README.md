# 🤖 LYAITEST — AI驱动的测试智能体平台

**LYAITEST** 是一个基于 LangGraph 和 FastAPI 构建的智能测试平台。它通过自然语言驱动 Agent 执行接口测试、Web 自动化测试和测试用例生成，并自动记录测试报告。系统支持完整的用户认证机制，数据按用户隔离。

---

## 🎯 项目背景与目标

传统测试工具需要编写脚本或手动操作，学习成本高、效率低。LYAITEST 通过 AI Agent 实现"用对话驱动测试"，让测试人员用自然语言描述测试需求，Agent 自动解析意图、调用测试工具、执行并生成报告。

---

## 🏗️ 项目架构

┌─────────────────────────────────────────────────────────────────┐
│ 用户界面 (Streamlit) │
│ 登录/注册 | 会话管理 | 聊天界面 | 报告查看 │
├─────────────────────────────────────────────────────────────────┤
│ API 网关 (FastAPI) │
│ JWT认证 | 路由分发 | 请求处理 │
├─────────────────────────────────────────────────────────────────┤
│ Agent 核心 (LangGraph) │
│ 意图识别 → 节点分流 → 工具执行 → 结果返回 │
├─────────────────────────────────────────────────────────────────┤
│ 工具层 (Tools) │
│ 接口测试工具 │ Web自动化工具 │ 用例生成工具 │
├─────────────────────────────────────────────────────────────────┤
│ 数据存储 (SQLite) │
│ 用户/会话/消息/知识库/测试报告 → 持久化存储 │
└─────────────────────────────────────────────────────────────────┘

### 核心模块说明

| 模块 | 技术栈 | 职责 |
|------|--------|------|
| 前端界面 | Streamlit | 提供登录注册、会话管理、聊天界面、报告查看 |
| API 网关 | FastAPI | 处理 HTTP 请求，JWT 认证，路由分发 |
| Agent 引擎 | LangGraph + LangChain | 意图识别、状态管理、工具调用编排 |
| 用户认证 | JWT + bcrypt | 用户注册、登录、Token 验证、数据隔离 |
| 测试工具 | requests + Playwright | 执行接口测试和 Web 自动化测试 |
| 数据存储 | SQLite | 保存用户、会话、消息、知识库、测试报告 |

---

## 📁 项目目录结构

```
lyaitest_upgrade/
├── app/
│   ├── routers/              # API 路由层
│   │   ├── auth.py           # 用户认证接口 (注册/登录)
│   │   ├── agent.py          # Agent 对话接口
│   │   ├── chat.py           # 聊天接口
│   │   ├── sessions.py       # 会话管理接口
│   │   ├── report.py         # 测试报告查询接口
│   │   ├── knowledge_base.py # 知识库管理接口
│   │   ├── api_test.py       # 接口测试管理接口
│   │   └── web_automation.py # Web自动化管理接口
│   ├── services/             # 业务逻辑层
│   │   ├── agent.py          # Agent 核心逻辑 (LangGraph)
│   │   ├── auth_service.py   # 用户认证服务
│   │   └── report_service.py # 测试报告存储服务
│   ├── dependencies/         # 依赖注入层
│   │   ├── __init__.py
│   │   └── auth.py           # Token 验证依赖
│   ├── models/               # 数据模型层
│   │   ├── session.py        # 会话数据模型
│   │   └── report.py         # 测试报告数据模型
│   ├── database.py           # SQLite 数据库连接与表初始化
│   └── main.py               # FastAPI 应用入口
├── app_frontend.py           # Streamlit 前端主程序
├── requirements.txt          # Python 依赖包列表
├── render.yaml               # Render 部署配置
├── .streamlit/config.toml    # Streamlit 主题配置
├── .env                      # 环境变量 (不上传 GitHub)
└── README.md                 # 项目文档
```

---

## ⚙️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 前端框架 | Streamlit |
| Agent 引擎 | LangGraph + LangChain |
| 大模型 | DeepSeek / 智谱 GLM |
| 用户认证 | JWT (python-jose) + bcrypt |
| 接口测试 | requests |
| Web 自动化 | Playwright |
| 数据库 | SQLite |
| 部署平台 | Render (后端) + Streamlit Cloud (前端) |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/LvRaya-bit/lyaitest_upgrade.git
cd lyaitest_upgrade/lyaitest_upgrade
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install
```

### 4. 配置环境变量

创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
ZHIPU_API_KEY=your_zhipu_api_key   # 如果用智谱
```

### 5. 启动后端服务

```bash
uvicorn app.main:app --reload
```

后端默认运行在 http://localhost:8000

### 6. 启动前端界面

```bash
streamlit run app_frontend.py
```

前端默认运行在 http://localhost:8501

### 7. 使用系统

1. 打开 http://localhost:8501
2. 注册新用户或登录已有账号
3. 登录成功后进入 AI 助手中心开始使用

---

## 🌐 上线部署（Render + Streamlit Cloud）

### 后端部署（Render）

1. 在 [Render](https://render.com) 创建 Web Service
2. 连接 GitHub 仓库 `lyaitest_upgrade`
3. Render 会自动识别 `render.yaml` 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4. 在 Render Dashboard → Environment 中配置：
   - `DEEPSEEK_API_KEY` = 你的 DeepSeek API Key
   - `JWT_SECRET_KEY` = 随机生成的密钥（用于JWT签名）
5. Render 会自动挂载 1GB 磁盘到 `/data`，SQLite 数据库保存在 `/data/lyaitest.db`

获取后端域名：`https://lyaitest-backend-xxxx.onrender.com`

### 前端部署（Streamlit Cloud）

1. 在 [Streamlit Cloud](https://streamlit.io/cloud) 创建 App
2. 连接同一个 GitHub 仓库
3. 在 App Settings → Secrets 中添加：
   ```toml
   api_base = "https://lyaitest-backend-xxxx.onrender.com/api/v1"
   ```
4. 部署完成后访问 Streamlit Cloud 提供的域名

### 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 必填 |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 自动生成 |
| `DATABASE_PATH` | SQLite 数据库路径 | `lyaitest.db` |
| `API_BASE` | 前端调用的后端地址 | `http://localhost:8001/api/v1` |

---

## 🔐 用户认证

系统实现了完整的用户认证机制：

- **用户注册**：用户名 + 密码，密码使用 bcrypt 加密存储
- **用户登录**：验证用户名和密码，返回 JWT Token（有效期 7 天）
- **Token 验证**：所有 API 请求通过 `Authorization: Bearer <token>` 头验证
- **数据隔离**：所有会话、消息、报告通过 user_id 关联，不同用户互不可见

---

## 📊 核心数据模型

| 表名 | 字段 | 说明 |
|------|------|------|
| users | id, username, password_hash, created_at | 用户信息 |
| sessions | id, user_id, name, created_at, knowledge_base_id | 会话信息 |
| messages | id, session_id, role, content, created_at | 聊天消息 |
| knowledge_base | id, user_id, name, description, file_path, created_at | 项目知识库 |
| interfaces | id, user_id, name, url, method, headers, params, body, created_at | 接口定义 |
| web_cases | id, user_id, name, description, steps, created_at | Web自动化用例 |
| reports | id, session_id, user_id, test_type, url, status_code, title, screenshot, error, created_at | 测试报告 |

---

## 🔗 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Streamlit 文档](https://docs.streamlit.io/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Playwright 文档](https://playwright.dev/python/)

---

## 📌 注意事项

- API Key 请通过环境变量配置，不要硬编码到代码中。
- SQLite 数据库文件 `lyaitest.db` 会在首次启动时自动生成。
- 部署到 Render 时，需要在后台配置环境变量。
- JWT Secret Key 当前为默认值，生产环境请修改 `app/services/auth_service.py` 中的 `SECRET_KEY`。