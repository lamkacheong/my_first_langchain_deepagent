# 研究助手 Agent (LangGraph)

一个基于 LangGraph 的专业研究助手，可以进行网络搜索并生成深入的研究报告。

## 功能特性

- 使用 Tavily API 进行智能网络搜索
- 基于 LangGraph 的工作流引擎
- 支持交互式开发和调试
- 可通过 `langgraph dev` 启动本地服务器

## 环境要求

- Python 3.12+
- uv 包管理器

## 快速开始

### 1. 配置环境变量

复制 `.env.example` 文件为 `.env`，并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下信息：

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
TAVILY_API_KEY=your_tavily_api_key_here
```

### 2. 安装依赖

使用 uv 安装项目依赖：

```bash
uv sync
uv pip install langgraph-cli
```

### 3. 运行 Agent

#### 方式 1: 使用 LangGraph Dev Server（推荐）

启动 LangGraph 开发服务器：

```bash
langgraph dev
```

这将启动一个本地服务器，通常在 `http://localhost:8123`，你可以通过 LangGraph Studio 或者 API 与 agent 交互。

#### 方式 2: 直接运行 Python 脚本

```bash
uv run python agent.py
```

## 项目结构

```
my_deepagent/
├── agent.py              # LangGraph agent 定义
├── langgraph.json        # LangGraph 配置文件
├── pyproject.toml        # 项目依赖配置
├── .env.example          # 环境变量示例
├── .env                  # 环境变量（需自行创建）
├── test_deepagent.ipynb  # 测试 notebook
└── README.md             # 本文件
```

## 使用示例

Agent 启动后，你可以向它提问，例如：

- "刘备和曹操各自的成长经历"
- "人工智能在医疗领域的最新应用"
- "比特币的技术原理和发展历史"

Agent 会自动：
1. 理解你的研究需求
2. 使用网络搜索工具收集相关信息
3. 分析和综合信息
4. 生成结构化的研究报告

## 工具说明

### internet_search

网络搜索工具，支持以下参数：

- `query`: 搜索查询关键词（必需）
- `max_results`: 最大返回结果数量（默认：5）
- `topic`: 搜索主题类型，可选 "general"、"news"、"finance"（默认："general"）
- `include_raw_content`: 是否包含原始内容（默认：False）

## 开发说明

- 项目使用 uv 进行依赖管理
- 使用清华大学镜像源加速下载
- Agent 基于 LangGraph 的 StateGraph 实现
- 支持工具调用和多轮对话

## 许可证

MIT
