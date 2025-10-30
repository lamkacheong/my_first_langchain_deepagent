"""LangGraph Research Agent - 一个专业的研究助手"""

import os
from typing import Literal

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from deepagents import create_deep_agent
from tavily import TavilyClient


# 初始化 Tavily 客户端
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


# Web search tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# 系统提示词
research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""
from langchain_anthropic import ChatAnthropic

# 创建 deep agent（langgraph dev 会使用这个）

model = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0,
    timeout=None,
    max_retries=2,
    # other params...
)

from langchain_openai import ChatOpenAI

model2 = ChatOpenAI(
    model="glm-4.6",
)
graph = create_deep_agent(
    tools=[internet_search],
    system_prompt=research_instructions,
    model=model2,
)


# 如果直接运行此文件，可以进行测试
if __name__ == "__main__":
    # 测试 agent
    print("测试 Research Agent...")
    print("=" * 50)

    test_query = "刘备和曹操各自的成长经历"

    for item in graph.stream(
        {"messages": [{"role": "user", "content": test_query}]},
        stream_mode="values"
    ):
        print(item)
