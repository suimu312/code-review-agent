# Code Review Agent · 代码审查助手

一个基于大语言模型的代码审查智能体，能够自动分析代码质量、发现潜在 Bug、给出改进建议。

**代码仓库**：[https://github.com/suimu312/code-review-agent](https://github.com/suimu312/code-review-agent)

## 功能特性

- **Agent 循环**：输入 → 推理 → 工具调用 → 输出，自主决定何时调用工具
- **三种工具**：
  - 📖 `read_file` — 读取本地代码文件内容
  - ▶ `execute_python` — 执行 Python 代码验证行为
  - 🔍 `analyze_code` — 静态分析代码质量指标
- **上下文记忆**：支持多轮对话，记住之前的审查内容
- **错误重试**：LLM 请求失败时指数退避重试
- **CLI 交互**：命令行界面，开箱即用

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

支持任何 OpenAI 兼容接口：

| 服务商 | BASE_URL | 模型示例 |
|--------|----------|----------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |

### 3. 运行

```bash
python main.py
```

### 4. 使用示例

```
你 > 帮我审查 examples/sample_code.py 这个文件

助手 > 我来读取文件内容进行审查...

（调用 read_file 工具）

助手 > ## 审查报告
...
```

你也可以直接粘贴代码：

```
你 > 审查这段代码：
def divide(a, b):
    return a / b
```

## 项目结构

```
code-review-agent/
├── main.py                  # CLI 入口
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量模板
├── README.md                # 本文件
├── Design.md                # 设计文档
├── agent/
│   ├── __init__.py
│   ├── agent.py             # Agent 核心循环
│   ├── llm.py               # LLM 客户端（带重试）
│   ├── memory.py            # 对话记忆管理
│   └── prompts.py            # System Prompt
├── tools/
│   ├── __init__.py
│   ├── file_reader.py        # 文件读取工具
│   ├── code_executor.py      # 代码执行工具
│   └── code_analyzer.py      # 静态分析工具
└── examples/
    └── sample_code.py        # 示例待审查代码
```

## 交互命令

| 命令 | 作用 |
|------|------|
| `:quit` / `:exit` | 退出程序 |
| `:clear` | 清空对话历史 |

## 技术栈

- **语言**：Python 3.10+
- **LLM 接口**：OpenAI SDK（兼容多家服务商）
- **无第三方 Agent 框架**：原生实现 Agent 循环，便于理解原理
