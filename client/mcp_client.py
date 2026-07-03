"""Small script that connects to the Programming Learning MCP server and
exercises its tools and resource. Used to test the server before wiring it
into an agent.

Run with: python3 client/mcp_client.py
"""

import asyncio
import sys
from pathlib import Path

from fastmcp import Client

SERVER_PATH = Path(__file__).resolve().parent.parent / "server" / "learning_server.py"

client = Client(str(SERVER_PATH))


async def main() -> None:
    async with client:
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        resources = await client.list_resources()
        print("Available resources:", [str(r.uri) for r in resources])

        print("\n--- search_topics('decorators') ---")
        result = await client.call_tool("search_topics", {"query": "decorators"})
        print(result.data)

        print("\n--- search_topics('nonexistent-topic-xyz') ---")
        result = await client.call_tool("search_topics", {"query": "nonexistent-topic-xyz"})
        print(result.data)

        print("\n--- get_topic_details('python-decorators') ---")
        result = await client.call_tool("get_topic_details", {"topic_id": "python-decorators"})
        print(result.data)

        print("\n--- get_topic_details('does-not-exist') ---")
        result = await client.call_tool("get_topic_details", {"topic_id": "does-not-exist"})
        print(result.data)

        print("\n--- resource topics://catalog ---")
        catalog = await client.read_resource("topics://catalog")
        print(catalog[0].text)


if __name__ == "__main__":
    asyncio.run(main())
