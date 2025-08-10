#!/usr/bin/env python3
"""
Anthropic Updates MCP Client Example

This script demonstrates how to interact with the Anthropic Updates MCP Server.
It shows various ways to fetch updates, model information, and other Anthropic
development data through the MCP protocol.
"""

import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import TextContent
except ImportError:
    logger.error("MCP client libraries not found. Please install with: pip install mcp")
    exit(1)

async def demonstrate_anthropic_updates():
    """
    Demonstrate various features of the Anthropic Updates MCP Server.
    """
    # Server parameters - adjust path as needed
    server_script = Path(__file__).parent / "server.py"
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)]
    )
    
    print("🚀 Starting Anthropic Updates MCP Client Demo")
    print("=" * 50)
    
    try:
        async with stdio_client(server_params) as (read, write):
            session = ClientSession(read, write)
            
            # 1. List monitored repositories
            print("\n📂 Listing monitored repositories...")
            result = await session.call_tool("list_monitored_repos", arguments={})
            repos_data = json.loads(result.content[0].text)
            print(f"Monitoring {repos_data['total_count']} repositories:")
            for repo in repos_data['monitored_repositories']:
                print(f"  - {repo}")
            
            # 2. Get latest updates from main Anthropic Python SDK
            print("\n🔄 Getting latest updates from anthropics/anthropic-sdk-python...")
            result = await session.call_tool("get_latest_updates", arguments={
                "repo": "anthropics/anthropic-sdk-python",
                "limit": 3
            })
            updates_data = json.loads(result.content[0].text)
            if isinstance(updates_data, str):
                print(updates_data)  # Error message
            else:
                print(f"Found {len(updates_data.get('latest_commits', []))} recent commits:")
                for commit in updates_data.get('latest_commits', []):
                    print(f"  • {commit['sha']}: {commit['message']} by {commit['author']}")
                
                if updates_data.get('latest_releases'):
                    print(f"Found {len(updates_data['latest_releases'])} recent releases:")
                    for release in updates_data['latest_releases']:
                        print(f"  • {release['tag_name']}: {release['name']}")
            
            # 3. Get model information
            print("\n🤖 Getting information about Claude models...")
            result = await session.call_tool("get_model_info", arguments={})
            models_data = json.loads(result.content[0].text)
            print(f"Found {models_data['total_models']} models:")
            for model_id, model_info in models_data['models'].items():
                print(f"  • {model_info['name']} ({model_id})")
                print(f"    - {model_info['description']}")
                print(f"    - Max tokens: {model_info['max_tokens']:,}")
            
            # 4. Search Anthropic documentation (this might hit rate limits without token)
            print("\n🔍 Searching Anthropic documentation for 'function calling'...")
            try:
                result = await session.call_tool("search_anthropic_docs", arguments={
                    "query": "function calling",
                    "limit": 3
                })
                search_data = json.loads(result.content[0].text)
                if isinstance(search_data, dict) and 'results' in search_data:
                    print(f"Found {search_data['total_found']} results:")
                    for item in search_data['results']:
                        print(f"  • {item['file_name']} in {item['repository']}")
                        print(f"    Path: {item['file_path']}")
                        print(f"    URL: {item['url']}")
                else:
                    print("Search result:", search_data)
            except Exception as e:
                print(f"Search failed (likely rate limited): {e}")
            
            # 5. Get repository statistics (this might hit rate limits without token)
            print("\n📊 Getting repository statistics...")
            try:
                result = await session.call_tool("get_repository_stats", arguments={
                    "repo": "anthropics/anthropic-cookbook"
                })
                stats_data = json.loads(result.content[0].text)
                if isinstance(stats_data, dict) and 'name' in stats_data:
                    print(f"Repository: {stats_data['name']}")
                    print(f"Description: {stats_data['description']}")
                    print(f"Language: {stats_data['language']}")
                    print(f"Stars: ⭐ {stats_data['stars']:,}")
                    print(f"Forks: 🍴 {stats_data['forks']:,}")
                    print(f"Open Issues: 🐛 {stats_data['open_issues']:,}")
                    print(f"Last Updated: {stats_data['updated_at']}")
                else:
                    print("Stats result:", stats_data)
            except Exception as e:
                print(f"Stats failed (likely rate limited): {e}")
            
    except Exception as e:
        logger.error(f"Error during demo: {e}")
        print(f"\n❌ Demo failed: {e}")
        return
    
    print("\n✅ Demo completed successfully!")
    print("=" * 50)

async def interactive_mode():
    """
    Interactive mode for exploring the MCP server.
    """
    server_script = Path(__file__).parent / "server.py"
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)]
    )
    
    print("🔧 Interactive Anthropic Updates MCP Client")
    print("Type 'help' for available commands, 'quit' to exit")
    print("=" * 50)
    
    async with stdio_client(server_params) as (read, write):
        while True:
            try:
                command = input("\nEnter command: ").strip()
                
                if command == "quit":
                    break
                elif command == "help":
                    print("Available commands:")
                    print("  repos - List monitored repositories")
                    print("  updates <repo> - Get latest updates for a repository")
                    print("  models - Show available models")
                    print("  search <query> - Search documentation")
                    print("  stats <repo> - Get repository statistics")
                    print("  changelog <repo> <days> - Get changelog")
                    print("  release <repo> - Get latest release notes")
                    print("  quit - Exit")
                elif command == "repos":
                    result = await read.call_tool("list_monitored_repos", {})
                    data = json.loads(result.content[0].text)
                    for repo in data['monitored_repositories']:
                        print(f"  - {repo}")
                elif command.startswith("updates "):
                    repo = command.split(" ", 1)[1]
                    result = await read.call_tool("get_latest_updates", {"repo": repo, "limit": 3})
                    data = json.loads(result.content[0].text)
                    if isinstance(data, dict) and 'latest_commits' in data:
                        for commit in data['latest_commits']:
                            print(f"  {commit['sha']}: {commit['message']}")
                    else:
                        print(data)
                elif command == "models":
                    result = await read.call_tool("get_model_info", {})
                    data = json.loads(result.content[0].text)
                    for model_id, info in data['models'].items():
                        print(f"  {info['name']} ({model_id}): {info['description']}")
                elif command.startswith("search "):
                    query = command.split(" ", 1)[1]
                    result = await read.call_tool("search_anthropic_docs", {"query": query, "limit": 3})
                    data = json.loads(result.content[0].text)
                    for item in data['results']:
                        print(f"  {item['file_name']} in {item['repository']}")
                elif command.startswith("stats "):
                    repo = command.split(" ", 1)[1]
                    result = await read.call_tool("get_repository_stats", {"repo": repo})
                    data = json.loads(result.content[0].text)
                    if isinstance(data, dict) and 'name' in data:
                        print(f"  {data['name']}: ⭐{data['stars']} 🍴{data['forks']} 🐛{data['open_issues']}")
                    else:
                        print(data)
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    print("\nGoodbye! 👋")

async def main():
    """
    Main function to run either demo or interactive mode.
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_mode()
    else:
        await demonstrate_anthropic_updates()

if __name__ == "__main__":
    asyncio.run(main())