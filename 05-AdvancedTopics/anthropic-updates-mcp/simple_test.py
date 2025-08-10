#!/usr/bin/env python3
"""
Simple test for the Anthropic Updates MCP Server
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def simple_test():
    """Simple test of the MCP server."""
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    print("Testing Anthropic Updates MCP Server...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            session = ClientSession(read, write)
            
            # List monitored repositories
            print("Calling list_monitored_repos...")
            result = await session.call_tool("list_monitored_repos", arguments={})
            print("Result:", result.content[0].text[:100] + "...")
            
            # Get model info 
            print("Calling get_model_info...")
            result = await session.call_tool("get_model_info", arguments={})
            print("Result:", result.content[0].text[:100] + "...")
            
            print("✅ Basic functionality working!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())