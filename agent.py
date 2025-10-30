"""LangGraph Research Agent - 一个专业的研究助手"""

import os
import json
import asyncio
import re
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from deepagents import create_deep_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


def load_mcp_config(config_path: str = "mcp_config.json") -> dict:
    """
    加载 MCP 配置文件并替换环境变量

    Args:
        config_path: 配置文件路径，默认为 mcp_config.json

    Returns:
        解析后的配置字典
    """
    # 获取配置文件的完整路径
    config_file = Path(__file__).parent / config_path

    if not config_file.exists():
        raise FileNotFoundError(f"MCP 配置文件不存在: {config_file}")

    # 读取配置文件
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 替换环境变量占位符
    def replace_env_vars(obj):
        """递归替换配置中的环境变量占位符"""
        if isinstance(obj, dict):
            return {k: replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # 替换 ${VAR_NAME} 格式的环境变量
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, obj)
            for var_name in matches:
                env_value = os.environ.get(var_name, "")
                if not env_value:
                    print(f"警告: 环境变量 {var_name} 未设置")
                obj = obj.replace(f"${{{var_name}}}", env_value)
            return obj
        else:
            return obj

    return replace_env_vars(config)


# 初始化 MCP 客户端配置
async def get_mcp_tools(config_path: str = "mcp_config.json"):
    """
    从配置文件获取 MCP 工具列表

    Args:
        config_path: MCP 配置文件路径

    Returns:
        tuple: (tools, client)
    """
    # 禁用代理以避免 SOCKS 代理问题
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"

    # 加载 MCP 配置
    config = load_mcp_config(config_path)

    # 获取服务器配置
    servers = config.get("servers", {})

    if not servers:
        raise ValueError("MCP 配置文件中没有定义任何服务器")

    print(f"加载了 {len(servers)} 个 MCP 服务器配置: {list(servers.keys())}")

    # 创建 MCP 客户端
    client = MultiServerMCPClient(servers)

    # 获取工具列表
    tools = await client.get_tools()

    print(f"成功加载了 {len(tools)} 个 MCP 工具")

    return tools, client


# 系统提示词 - 动态生成以反映可用的 MCP 工具
async def get_research_instructions(tools):
    """根据 MCP 工具动态生成指令"""
    tool_descriptions = []

    for tool in tools:
        tool_name = tool.name
        tool_desc = tool.description
        tool_descriptions.append(f"## `{tool_name}`\n\n{tool_desc}")

    tools_section = "\n\n".join(tool_descriptions)

    return f"""You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.

You have access to the following MCP tools as your primary means of gathering information:

{tools_section}

Use these tools effectively to conduct comprehensive research and provide accurate, well-sourced information.
"""
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


# 异步初始化 agent
async def create_agent():
    """创建配置了 MCP 工具的 deep agent"""
    # 获取 MCP 工具
    tools, client = await get_mcp_tools()

    # 获取动态生成的指令
    instructions = await get_research_instructions(tools)

    # 创建模型
    model = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0,
        timeout=None,
        max_retries=2,
    )

    model2 = ChatOpenAI(
        model="glm-4.6",
    )

    # 创建 agent
    graph = create_deep_agent(
        tools=tools,
        system_prompt=instructions,
        model=model2,
    )

    return graph, client


# 为 langgraph dev 提供延迟初始化的 graph
# 使用函数而不是立即初始化，避免在导入时创建事件循环
def _create_graph_sync():
    """同步方式创建 graph（仅用于 langgraph dev）"""
    import nest_asyncio
    nest_asyncio.apply()  # 允许嵌套事件循环

    graph_instance, client = asyncio.run(create_agent())
    return graph_instance


# langgraph dev 会导入这个 graph
# 使用延迟初始化以避免导入时的问题
try:
    graph = _create_graph_sync()
except Exception as e:
    print(f"警告: 初始化 graph 失败: {e}")
    print("将在运行时重新尝试初始化")
    graph = None


# 如果直接运行此文件，可以进行测试
if __name__ == "__main__":
    async def main():
        # 测试 agent
        print("测试 Research Agent...")
        print("=" * 50)

        graph, client = await create_agent()

        test_query = "刘备和曹操各自的成长经历"

        # 使用异步流式处理
        async for item in graph.astream(
            {"messages": [{"role": "user", "content": test_query}]},
            stream_mode="values"
        ):
            print(item)

        # 清理
        await client.cleanup()

    asyncio.run(main())
