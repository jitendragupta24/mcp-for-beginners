#!/usr/bin/env python3
"""
Anthropic Updates Demo

This script demonstrates the core functionality of the Anthropic Updates MCP Server
by calling the tools directly. This is useful for testing and demonstration purposes
without needing to set up a full MCP client-server connection.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import our server functions
from server import (
    list_monitored_repos,
    get_model_info,
    get_latest_updates,
    get_repository_stats,
    search_anthropic_docs,
    get_changelog,
    get_release_notes
)

class MockContext:
    """Mock context for testing."""
    pass

async def demo_anthropic_updates():
    """
    Demonstrate the Anthropic Updates functionality.
    """
    print("🚀 Anthropic Updates MCP Server Demo")
    print("=" * 50)
    
    ctx = MockContext()
    
    # 1. List monitored repositories
    print("\n📂 Listing monitored repositories...")
    try:
        result = await list_monitored_repos(ctx)
        data = json.loads(result)
        print(f"Monitoring {data['total_count']} repositories:")
        for repo in data['monitored_repositories']:
            print(f"  - {repo}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Get model information
    print("\n🤖 Getting information about Claude models...")
    try:
        result = await get_model_info(ctx)
        data = json.loads(result)
        print(f"Found {data['total_models']} models:")
        for model_id, model_info in data['models'].items():
            print(f"  • {model_info['name']} ({model_id})")
            print(f"    - {model_info['description']}")
            print(f"    - Max tokens: {model_info['max_tokens']:,}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Search for specific model
    print("\n🔍 Getting specific model information...")
    try:
        result = await get_model_info(ctx, model_name="claude-3-5-sonnet")
        data = json.loads(result)
        print(f"Model: {data['name']}")
        print(f"Description: {data['description']}")
        print(f"Release Date: {data['release_date']}")
        print(f"Strengths: {', '.join(data['strengths'])}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Test repository validation
    print("\n🔍 Testing repository validation...")
    try:
        result = await get_latest_updates(ctx, repo="invalid/repo")
        print(f"Validation result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. GitHub API examples (will work with internet connection)
    print("\n🌐 Testing with real GitHub API (may hit rate limits)...")
    
    # Try to get repository stats
    try:
        print("Getting repository statistics for anthropics/anthropic-cookbook...")
        result = await get_repository_stats(ctx, repo="anthropics/anthropic-cookbook")
        if "Error" in result:
            print(f"Rate limited or error: {result}")
        else:
            data = json.loads(result)
            if 'name' in data:
                print(f"✅ Repository: {data['name']}")
                print(f"   Stars: ⭐ {data['stars']:,}")
                print(f"   Language: {data['language']}")
                print(f"   Last updated: {data['updated_at'][:10]}")
            else:
                print(f"Unexpected response: {result[:200]}...")
    except Exception as e:
        print(f"Repository stats failed: {e}")
    
    # Try to get latest updates
    try:
        print("\nGetting latest updates from anthropics/anthropic-sdk-python...")
        result = await get_latest_updates(ctx, repo="anthropics/anthropic-sdk-python", limit=2)
        if "Error" in result:
            print(f"Rate limited or error: {result}")
        else:
            data = json.loads(result)
            if 'latest_commits' in data:
                print(f"✅ Found {len(data['latest_commits'])} recent commits:")
                for commit in data['latest_commits']:
                    print(f"   • {commit['sha']}: {commit['message'][:60]}...")
            else:
                print(f"Unexpected response: {result[:200]}...")
    except Exception as e:
        print(f"Latest updates failed: {e}")
    
    print("\n✅ Demo completed!")
    print("\nNote: GitHub API calls may be rate limited without authentication.")
    print("To increase rate limits, add GITHUB_TOKEN to a .env file.")
    print("\nTo test the full MCP server:")
    print("  python server.py")
    print("\nTo run the MCP client (when server initialization is fixed):")
    print("  python client.py")

if __name__ == "__main__":
    asyncio.run(demo_anthropic_updates())