import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    mcp_url = "http://localhost:8000/mcp"
    headers = {}

    async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            # tool_result = await session.list_tools()
            # print("Available tools:")
            # for tool in tool_result.tools:
            #     print(f"  - {tool.name}: {tool.description}")
            # print()
            
            # Test 1: Use add_numbers tool
            print("=== Test 1: Adding numbers ===")
            try:
                result = await session.call_tool("add_numbers", {"a": 10, "b": 25})
                print(f"Result of add_numbers(10, 25): {result.content[0].text}")
            except Exception as e:
                print(f"Error calling add_numbers: {e}")

if __name__ == "__main__":
    asyncio.run(main())
