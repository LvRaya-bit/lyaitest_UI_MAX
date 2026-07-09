# Web Agent 智能测试平台 — 面试巩固与进阶学习指南

> 本文档基于你当前在 DeepSeek 对话中完成的第一天学习内容（API 基础调用、messages 结构、openai 库通用标准、大模型调用核心流程），以**模拟技术面试官**的视角设计了一套"巩固复习 + 进阶引导"问答。
> 
> 每道题均采用**"面试官提问 → 你的思考空间 → 参考答案 → 深度解析"**的结构。建议你先盖住答案，自己尝试回答，再对照解析查漏补缺。

---

# 第一部分：面试回顾（第一天知识点）

## 一、温场回顾（记忆级）

### 面试题 1

**面试官**：调用 DeepSeek API 前，我们需要安装哪个 Python 库？

<details>
<summary>点击查看参考答案</summary>

**答案**：`openai`

```bash
pip install openai
```

</details>

**深度解析**：
虽然我们要调用的是 DeepSeek 的模型，但使用的是 `openai` 这个 Python 库。这是因为 openai 库已经成为大模型 API 的**通用标准接口**（行业事实标准）。DeepSeek、智谱、阿里通义等厂商都兼容这套标准，方便开发者无缝迁移。这就像手机充电接口统一成了 Type-C，不管你用哪个品牌的充电器，插口都是一样的。

---

### 面试题 2

**面试官**：除了安装库，调用前还需要准备什么关键凭证？使用时要注意什么安全问题？

<details>
<summary>点击查看参考答案</summary>

**答案**：**API Key**。从 DeepSeek 官网控制台获取。使用时注意不要硬编码在代码中提交到 Git，建议使用环境变量或配置文件管理。

</details>

**深度解析**：
API Key 相当于你的"身份令牌"，服务器靠它识别是谁在调用、扣谁的额度。常见的安全做法：
- 使用环境变量：`api_key = os.environ.get("DEEPSEEK_API_KEY")`
- 使用 `.env` 文件 + `python-dotenv` 加载
- 绝对不要把 Key 上传到 GitHub（可以用 `.gitignore` 忽略配置文件）

---

### 面试题 3

**面试官**：用一句话描述大模型 API 调用的核心流程。这个过程中，客户端和服务器各自承担了什么角色？

<details>
<summary>点击查看参考答案</summary>

**答案**：核心流程是 **"你的代码发送文本 → 远程服务器上的大模型处理 → 返回结果文本"**。

- **客户端（你的电脑）**：负责构造请求、发送文本、接收并展示结果
- **服务器（DeepSeek）**：负责运行大模型程序、执行推理计算、生成回复

</details>

**深度解析**：
调用大模型本质上就是一个 HTTP 请求——你的代码把文本（messages）打包成 JSON，通过 HTTP POST 发到 `api.deepseek.com`，服务器上的 GPU 集群运行大模型进行数学计算（预测下一个词的概率分布），然后把生成的文本返回给你。你的电脑只负责"发信"和"收信"，真正的"思考"发生在远程服务器上。这也是为什么叫 **API（应用程序接口）** —— 你通过接口让别的程序为你工作。

---

## 二、深度拷问（理解级 + 应用级）

### 面试题 4（代码填空）

**面试官**：来，现场写一段代码。补全以下 DeepSeek API 调用的核心代码：

```python
import openai

# ① 创建客户端时，需要设置哪两个关键参数来适配 DeepSeek？
client = openai.OpenAI(
    base_url="__________",
    api_key="__________"
)

# ② 调用对话接口的方法名是什么？
response = client.__________.create(
    model="__________",
    messages=[
        {"role": "__________", "content": "你是一个专业的测试工程师"},
        {"role": "__________", "content": "请帮我生成一条登录接口的测试用例"}
    ]
)

# ③ 如何从响应中提取模型的回复文本？
answer = response.choices[0].__________.content
```

<details>
<summary>点击查看参考答案</summary>

**答案**：
- ① `base_url="https://api.deepseek.com"`，`api_key="sk-..."`
- ② `chat.completions`，`deepseek-chat`
- ③ `message`

**完整代码**：

```python
import openai

client = openai.OpenAI(
    base_url="https://api.deepseek.com",
    api_key="sk-xxxxxxxxxxxxxxxx"  # 替换为你的真实 Key
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个专业的测试工程师"},
        {"role": "user", "content": "请帮我生成一条登录接口的测试用例"}
    ]
)

answer = response.choices[0].message.content
print(answer)
```

</details>

**深度解析**：
- `base_url` 指向 DeepSeek 的服务器地址（`https://api.deepseek.com`），而不是 OpenAI 的默认地址
- `deepseek-chat` 是 DeepSeek 的对话模型标识（类似 OpenAI 的 `gpt-4`）
- `chat.completions.create()` 是 openai 库中调用对话补全接口的标准方法
- `choices[0].message.content` 是 OpenAI 标准响应结构，DeepSeek 完全兼容这一格式

---

### 面试题 5（概念辨析 + 填空）

**面试官**：`messages` 参数中的三个 role（system / user / assistant）各自的作用是什么？请完成下表，并给出一个形象类比。

| Role | 作用描述 | 类比（帮助记忆） |
|------|----------|------------------|
| system | ________________ | 像剧场的 ________________ |
| user | ________________ | 像 ________________ |
| assistant | ________________ | 像 ________________ |

<details>
<summary>点击查看参考答案</summary>

**答案**：

| Role | 作用描述 | 类比 |
|------|----------|------|
| system | 设定模型的行为准则、角色定位、回答风格。优先级最高，贯穿整个对话 | 像剧场的**导演**，定剧本、定基调 |
| user | 用户的实际问题或指令，每次对话的核心输入 | 像**观众/顾客**，提出具体需求 |
| assistant | AI 生成的回复内容，用于多轮对话时提供上下文 | 像**演员/服务员**，根据指令表演/服务 |

</details>

**深度解析**：
- **system** 的消息虽然在 messages 数组里，但它不会被显示给用户，而是作为"背景设定"告诉模型应该怎么说话。比如 `"你是专业的测试工程师，擅长生成边界值测试用例"`，模型后续的回答风格就会偏向专业测试视角。
- **user** 是最核心的输入，没有 user 消息，模型不知道要回答什么。
- **assistant** 在多轮对话中非常重要——因为**大模型本身没有记忆**，你必须把之前模型的回复也放到 messages 里，它才能"记得"之前聊过什么。这也是为什么多轮对话的 messages 会越来越长。

---

### 面试题 6（设计思想）

**面试官**：为什么说 openai 库是一个"通用标准"？如果明天要换成通义千问或智谱 GLM，代码上大概需要改哪些地方？

<details>
<summary>点击查看参考答案</summary>

**答案**：
openai 库定义了一套标准的调用方式（请求格式、参数命名、响应结构），许多非 OpenAI 的模型服务商（DeepSeek、智谱、阿里通义等）为了让开发者能无缝迁移，都选择兼容这套标准。因此，切换厂商时通常只需要改三个地方：

1. `base_url`（服务商的 API 地址）
2. `api_key`（新服务商的密钥）
3. `model`（新服务商的模型名称）

messages 结构、调用方法、响应格式基本保持一致。

</details>

**深度解析**：
这体现了**接口标准化**的巨大价值。想象一下，如果每个厂商都用自己的 SDK、自己的参数命名、自己的响应格式，开发者每换一个模型就要重写一套代码，成本极高。OpenAI SDK 凭借其先发优势成为了事实标准，后来者为了降低开发者的迁移成本，都选择"对齐"这套接口。这意味着：**你现在通过 DeepSeek 学到的这套调用方法，知识是可以直接复用的**，未来切换到其他主流大模型，代码结构几乎一样。

---

### 面试题 7（场景分析）

**面试官**：以下是一个多轮对话的 messages 结构，请回答：第三轮对话中模型新的回复应该放在哪里？为什么？

```python
messages = [
    {"role": "system", "content": "你是测试专家"},
    {"role": "user", "content": "生成登录用例"},
    {"role": "assistant", "content": "① 正常登录 ② 密码错误..."},
    {"role": "user", "content": "再补充一下异常场景"},
    # 模型新的回复应该放在哪里？
]
```

<details>
<summary>点击查看参考答案</summary>

**答案**：新的 assistant 回复应该追加到 messages 数组的末尾：

```python
messages.append({"role": "assistant", "content": "③ 用户名不存在 ④ 密码为空 ⑤ 验证码错误..."})
```

</details>

**深度解析**：
这道题考察的是**大模型的"无状态"特性**。大模型本身不保存任何对话历史，每次 API 调用都是独立的。你传给它的 `messages` 数组就是它的全部"记忆"。所以多轮对话时，必须将完整的对话历史（包括之前的 user 提问和 assistant 回复）全部传入，模型才能根据上下文给出连贯的回答。如果漏掉了之前的 assistant 回复，模型就会"失忆"，不知道之前聊过什么。

---

# 第二部分：进阶预习（第二天及后续知识点）

## 三、参数调优类

### 面试题 8（引出 temperature）

**面试官**：刚才的代码里没有设置 temperature。如果我希望模型生成测试用例时更有创造性，能发现更多边界情况和异常场景，应该调哪个参数？它的取值范围和影响是什么？

<details>
<summary>点击查看参考答案</summary>

**答案**：应该调节 `temperature` 参数。

- **作用**：控制模型输出的随机性和创造性
- **取值范围**：0 ~ 2（常用 0.1 ~ 1.0）
- **影响**：
  - **低 temperature（如 0.2）**：输出更稳定、更确定，适合生成标准、规范的测试用例
  - **高 temperature（如 0.8）**：输出更多样、更有创意，适合头脑风暴和探索异常场景

**Web Agent 测试场景建议**：
- 生成标准功能用例：`temperature=0.3`
- 探索边界值和异常场景：`temperature=0.7`

</details>

**深度解析**：
`temperature` 本质上控制的是模型预测下一个词时的概率分布"平滑程度"。温度越低，模型越倾向于选择概率最高的词（保守、确定）；温度越高，概率分布被拉平，模型更可能"冒险"选择概率较低但新颖的词（创造性、多样性）。在测试用例生成场景中，低 temperature 保证用例的规范性和可执行性，高 temperature 则能帮你想到平时容易忽略的边界情况。

---

### 面试题 9（引出 max_tokens）

**面试官**：如果模型回复特别长，或者你想控制每次调用的成本，应该用什么参数限制输出长度？请说明它的单位和实际影响。

<details>
<summary>点击查看参考答案</summary>

**答案**：使用 `max_tokens` 参数。

- **作用**：限制模型一次回复的最大 token 数量
- **单位**：token（不是字符数）。1 个 token 约等于 1~2 个汉字，或 0.75 个英文单词
- **实际影响**：
  - 控制生成内容的总长度
  - 直接影响调用成本（API 按 token 数量计费）
  - 防止模型生成过长的冗余回复

**Web Agent 测试场景建议**：
- 生成测试报告摘要：`max_tokens=500`
- 生成完整测试用例集：`max_tokens=2000`

</details>

**深度解析**：
Token 是大模型处理文本的最小单位。英文中一个单词可能被拆成多个 token（比如 "unbelievable" 可能被拆成 "un" + "believ" + "able"），中文中一个汉字通常对应 1~2 个 token。`max_tokens` 不仅限制输出长度，也是成本控制的重要手段。在 Web Agent 平台中，你可以根据不同的测试任务动态调整这个值——摘要类任务给少一点，复杂用例生成给多一点。

---

### 面试题 10（temperature vs top_p）

**面试官**：`temperature` 和 `top_p` 都能控制输出多样性，它们有什么区别？面试时经常一起问，建议只调其中一个。

<details>
<summary>点击查看参考答案</summary>

**答案**：

| 参数 | 控制方式 | 本质区别 |
|------|----------|----------|
| `temperature` | 直接调节概率分布的"平滑程度" | 对整体概率分布进行温度缩放，影响所有词的选择倾向 |
| `top_p`（核采样） | 动态截断，只从累计概率达到 p 的最小词集合中采样 | 先筛选出一个"高质量候选词集合"，再在这个集合内随机选择 |

- **官方建议**：一般只调其中一个，不要同时大幅调整两者
- **常用搭配**：`temperature=0.7` + `top_p=1.0`（默认），或 `temperature=1.0` + `top_p=0.9`

**Web Agent 测试场景建议**：
- 固定格式用例生成：`top_p=0.1`（高确定性）
- 探索性测试场景头脑风暴：`top_p=0.9`（高多样性）

</details>

**深度解析**：
可以这样想：temperature 是"让所有人都有机会被选中"（把概率分布摊平），而 top_p 是"只从精英群体中选"（先过滤掉概率太低的词，再在剩余的高概率词中随机）。两者都能增加多样性，但机制不同。在实际使用中，**固定任务用低 top_p，创造性任务用高 top_p**，比单纯调 temperature 更可控。

---

## 四、高级特性类

### 面试题 11（引出 stream）

**面试官**：你在 ChatGPT 网页版聊天时，字是一个一个"蹦"出来的。如果用 API 实现这种实时打字效果，应该怎么做？底层用的是什么协议？

<details>
<summary>点击查看参考答案</summary>

**答案**：设置 `stream=True`，底层使用 **SSE（Server-Sent Events）** 协议。

**代码对比**：

```python
# 非流式（默认）
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)
print(response.choices[0].message.content)

# 流式
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=True  # 开启流式输出
)

for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

</details>

**深度解析**：
当 `stream=True` 时，服务器不会等全部内容生成完再返回，而是生成一部分就发一部分（通过 SSE 协议持续推送）。客户端收到的是一个迭代器，需要逐 chunk 读取并实时展示。在 Web Agent 测试平台中，流式输出有两个核心价值：
1. **提升用户体验**：用户不用干等着，能实时看到模型在"思考"和"生成"
2. **减少等待焦虑**：长时间任务（如生成大量测试用例）时，逐字显示让过程更有反馈感

---

### 面试题 12（引出 function calling）

**面试官**：Web Agent 的核心能力之一是让大模型"调用工具"。比如模型自己判断需要查询数据库、调用接口、执行测试脚本。这在 API 层面怎么实现？请描述完整流程。

<details>
<summary>点击查看参考答案</summary>

**答案**：通过 `function calling`（函数调用 / 工具调用）实现。

**完整流程**：

1. **定义工具**：开发者预定义一组函数列表，包含函数名、功能描述、参数 schema（JSON Schema 格式）
2. **传入模型**：在 API 调用时通过 `tools` 参数把这些函数定义传给模型
3. **模型判断**：模型根据用户请求，判断是否需要调用某个工具
4. **生成参数**：如果需要调用，模型会输出一个特殊的 `tool_calls` 响应，包含函数名和参数 JSON
5. **开发者执行**：开发者在本地执行对应的函数，拿到结果
6. **结果回传**：将函数执行结果以 `tool` role 的消息再次传给模型
7. **模型总结**：模型基于函数返回结果，生成最终的回答

**简化代码示例**：

```python
# 1. 定义工具
functions = [
    {
        "name": "run_pytest",
        "description": "运行 pytest 测试并返回结果",
        "parameters": {
            "type": "object",
            "properties": {
                "test_file": {"type": "string", "description": "测试文件路径"}
            },
            "required": ["test_file"]
        }
    }
]

# 2. 传给模型
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=functions
)

# 3. 检查是否需要调用工具
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    # 4. 本地执行函数
    if function_name == "run_pytest":
        result = run_pytest(arguments["test_file"])
    
    # 5. 将结果回传给模型
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(result)
    })
    
    # 6. 获取最终回答
    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
```

</details>

**深度解析**：
Function Calling 是构建 Web Agent 的**核心能力**。它让大模型从"只会说话"升级为"能动手"——模型可以根据用户意图，自主决定调用什么工具、传什么参数。在智能测试平台中，这个功能可以实现：
- 自动生成测试用例后，**自动调用 pytest 执行**
- 根据报错信息，**自动查询历史 Bug 库**
- 根据测试结果，**自动发送通知到钉钉/飞书**
- 根据需求变更，**自动更新对应的测试用例**

---

### 面试题 13（综合设计题）

**面试官**：假设你要开发一个 Web Agent 智能测试平台，核心需求是：根据需求文档自动生成测试用例，并自动调用接口执行后返回测试结果。请设计一个完整的 API 调用方案，说明你会用到哪些参数、role 和特性，以及为什么这么设计。

<details>
<summary>点击查看参考答案</summary>

**答案**：

**方案设计要点**：

1. **Role 设计**：
   - `system`：设定"资深测试工程师"身份，明确输出格式（pytest 代码格式）
   - `user`：传入需求文档内容
   - `assistant`：模型的用例生成回复
   - `tool`：pytest 执行结果的回传

2. **参数配置**：
   - `model="deepseek-chat"`：选择支持 function calling 的模型
   - `temperature=0.3`：保证用例生成的规范性和可执行性
   - `max_tokens=2000`：控制单次输出长度，避免过长
   - `stream=True`：实时展示用例生成过程，提升用户体验
   - `tools=[run_pytest, query_api_doc]`：预定义测试执行和文档查询工具

3. **完整交互流程**：

```
用户上传需求文档
    ↓
System: "你是测试专家，用 pytest 格式生成用例"
    ↓
User: 需求文档内容
    ↓
模型生成 pytest 测试代码 (stream=True 实时展示)
    ↓
模型判断需要执行测试 → function calling 调用 run_pytest
    ↓
本地执行 pytest，返回结果
    ↓
结果以 tool role 回传模型
    ↓
模型分析测试结果，生成测试报告
    ↓
返回最终报告给用户
```

</details>

**深度解析**：
这道题考察的是**综合运用能力**。一个完整的 Web Agent 测试平台不是简单的"调一次 API"，而是一个**多轮交互、工具调用、状态管理**的复杂系统。设计时需要考虑：
- **稳定性**：低 temperature 保证代码可运行
- **实时性**：stream 让用户有反馈
- **自动化**：function calling 让平台能真正"动起来"
- **上下文管理**：多轮 messages 维护完整的测试会话历史

---

# 第三部分：代码示例合集

## 示例 1：最简基础调用

```python
import openai

client = openai.OpenAI(
    base_url="https://api.deepseek.com",
    api_key="your-api-key"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个专业的测试工程师"},
        {"role": "user", "content": "请生成一个登录接口的 pytest 测试用例"}
    ]
)

print(response.choices[0].message.content)
```

## 示例 2：带参数调优的调用

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    temperature=0.3,      # 低温度，保证用例规范性
    max_tokens=2000,      # 限制输出长度
    top_p=0.9             # 适度多样性
)
```

## 示例 3：流式输出

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=True
)

full_content = ""
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        full_content += content
        print(content, end="", flush=True)
```

## 示例 4：多轮对话上下文维护

```python
messages = [
    {"role": "system", "content": "你是测试专家"},
    {"role": "user", "content": "生成登录用例"}
]

# 第一轮
response = client.chat.completions.create(
    model="deepseek-chat", messages=messages
)
reply = response.choices[0].message.content
messages.append({"role": "assistant", "content": reply})

# 第二轮：用户追问
messages.append({"role": "user", "content": "再补充异常场景"})
response = client.chat.completions.create(
    model="deepseek-chat", messages=messages
)
print(response.choices[0].message.content)
```

## 示例 5：Function Calling 完整流程

```python
import json

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "run_pytest",
            "description": "运行 pytest 测试文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"}
                },
                "required": ["file_path"]
            }
        }
    }
]

messages = [
    {"role": "system", "content": "你是自动化测试助手"},
    {"role": "user", "content": "生成登录测试用例并执行"}
]

# 第一次调用
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)

message = response.choices[0].message

# 检查是否需要调用工具
if message.tool_calls:
    # 执行工具
    tool_call = message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    result = run_pytest(args["file_path"])
    
    # 将工具调用和结果加入上下文
    messages.append(message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(result)
    })
    
    # 第二次调用获取最终回复
    final = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    print(final.choices[0].message.content)
```

---

# 第四部分：核心知识点速查表

| 参数/概念 | 作用 | 常用取值 | Web Agent 测试场景建议 |
|-----------|------|----------|------------------------|
| `base_url` | 指定 API 服务器地址 | `https://api.deepseek.com` | 切换厂商时修改 |
| `api_key` | 身份认证令牌 | `sk-...` | 使用环境变量管理，勿硬编码 |
| `model` | 指定模型版本 | `deepseek-chat` | 根据任务选择不同模型 |
| `messages` | 对话消息数组 | `[{role, content}, ...]` | 多轮对话需维护完整历史 |
| `system` role | 设定 AI 身份和行为准则 | `"你是测试工程师"` | 统一放在 messages 第一项 |
| `user` role | 用户输入/提问 | 具体问题内容 | 每次调用的核心输入 |
| `assistant` role | AI 回复内容 | 模型的生成结果 | 多轮对话时必须回传 |
| `temperature` | 控制输出随机性/创造性 | 0 ~ 2（常用 0.3~0.8） | 规范用例 0.3，头脑风暴 0.7 |
| `max_tokens` | 限制最大输出长度 | 512 ~ 4096 | 摘要 500，用例集 2000 |
| `top_p` | 核采样，控制候选词范围 | 0 ~ 1（常用 0.1~0.9） | 固定任务 0.1，探索任务 0.9 |
| `stream` | 开启流式实时输出 | `True` / `False` | 用户交互场景建议开启 |
| `function calling` | 让模型调用外部工具 | `tools` 参数定义 | Web Agent 的核心能力 |

---

# 第五部分：学习路线图

## 已掌握（第一天）
- [x] openai 库安装与环境搭建
- [x] DeepSeek API Key 获取与客户端配置
- [x] 基础 API 调用（chat.completions.create）
- [x] messages 数组结构与三个 role 的作用
- [x] openai 库作为通用标准的原理
- [x] 大模型调用的核心流程（发送文本 → 处理 → 返回）
- [x] 多轮对话的上下文维护机制

## 待学习（后续优先级排序）

### 高优先级（建议立即学习）
- [ ] **temperature / max_tokens / top_p**：控制输出质量和成本的核心参数
- [ ] **stream 流式输出**：提升用户体验的必备技能
- [ ] **function calling**：Web Agent 让大模型"动手"的核心能力

### 中优先级（后续深入）
- [ ] **JSON Mode / Structured Output**：强制模型按指定格式输出（如 JSON），便于程序解析
- [ ] **Embedding 向量**：文本向量化，用于测试用例相似度检索、Bug 去重
- [ ] **RAG（检索增强生成）**：让大模型基于私有知识库（需求文档、历史用例）生成更准确的测试内容

### 高优先级（平台化必备）
- [ ] **Prompt Engineering 进阶**：Few-shot、Chain-of-Thought、ReAct 等高级提示技巧
- [ ] **Agent 架构设计**：规划（Planning）→ 执行（Action）→ 观察（Observation）的循环
- [ ] **测试领域特化**：测试用例模板设计、断言自动生成、测试数据构造

---

> **面试心法**：面试官不仅考察"你会不会调 API"，更关注你**是否理解背后的设计思想**（如通用标准、无状态设计）和**能否将技术应用到具体场景**（如测试平台架构设计）。复习时多问自己"为什么这样设计"、"如果换成另一个场景我会怎么调整"，比单纯背代码更有效。
