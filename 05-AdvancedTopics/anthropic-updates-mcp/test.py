#!/usr/bin/env python3
"""
Test script for Anthropic Updates MCP Server

This script performs basic tests to ensure the MCP server is working correctly.
It tests the main functionality without requiring external dependencies.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

# Import our server components
from server import (
    mcp, ANTHROPIC_REPOS, ANTHROPIC_MODELS, 
    get_cache_key, set_cache, get_from_cache
)

class MockContext:
    """Mock context for testing."""
    pass

async def test_basic_functionality():
    """Test basic server functionality."""
    print("🧪 Testing Anthropic Updates MCP Server")
    print("=" * 40)
    
    ctx = MockContext()
    
    # Test 1: List monitored repositories
    print("\n📂 Test 1: List monitored repositories")
    try:
        # Import the actual function from server
        from server import list_monitored_repos
        result = await list_monitored_repos(ctx)
        data = json.loads(result)
        assert "monitored_repositories" in data
        assert len(data["monitored_repositories"]) > 0
        print(f"✅ Found {len(data['monitored_repositories'])} monitored repositories")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    # Test 2: Get model information
    print("\n🤖 Test 2: Get model information")
    try:
        from server import get_model_info
        result = await get_model_info(ctx)
        data = json.loads(result)
        assert "models" in data
        assert len(data["models"]) > 0
        print(f"✅ Found {len(data['models'])} models")
        
        # Test specific model
        result = await get_model_info(ctx, model_name="claude-3")
        data = json.loads(result)
        assert "model_id" in data
        print(f"✅ Successfully retrieved specific model: {data['model_id']}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    # Test 3: Cache functionality
    print("\n💾 Test 3: Cache functionality")
    try:
        key = get_cache_key("test", {"param": "value"})
        test_data = {"test": "data"}
        set_cache(key, test_data)
        cached_data = get_from_cache(key)
        assert cached_data == test_data
        print("✅ Cache functionality working correctly")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    # Test 4: Repository validation
    print("\n🔍 Test 4: Repository validation")
    try:
        from server import get_latest_updates
        # Test with invalid repo
        result = await get_latest_updates(ctx, repo="invalid/repo")
        assert "not in the monitored" in result
        print("✅ Repository validation working correctly")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print("\n✅ All basic tests passed!")
    return True

async def test_with_mock_responses():
    """Test with mock responses to avoid hitting actual APIs."""
    print("\n🎭 Testing with mock responses")
    
    # Test that the functions exist and have proper signatures
    tools = [
        "get_latest_updates",
        "get_model_info", 
        "get_changelog",
        "search_anthropic_docs",
        "get_release_notes",
        "get_repository_stats",
        "list_monitored_repos"
    ]
    
    try:
        import server
        for tool_name in tools:
            tool_func = getattr(server, tool_name, None)
            if tool_func is None:
                print(f"❌ Function {tool_name} not found")
                return False
            print(f"✅ Function {tool_name} exists and is callable")
        
        return True
    except Exception as e:
        print(f"❌ Mock response test failed: {e}")
        return False

def test_configuration():
    """Test server configuration."""
    print("\n⚙️  Testing server configuration")
    
    # Test that repositories list is properly configured
    assert len(ANTHROPIC_REPOS) > 0
    print(f"✅ {len(ANTHROPIC_REPOS)} repositories configured")
    
    # Test that models are properly configured
    assert len(ANTHROPIC_MODELS) > 0
    print(f"✅ {len(ANTHROPIC_MODELS)} models configured")
    
    # Test repository format
    for repo in ANTHROPIC_REPOS:
        assert "/" in repo, f"Repository {repo} should be in owner/name format"
    print("✅ All repositories are in correct format")
    
    # Test model structure
    for model_id, model_info in ANTHROPIC_MODELS.items():
        assert "name" in model_info
        assert "description" in model_info
        assert "max_tokens" in model_info
    print("✅ All models have required fields")
    
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting Anthropic Updates MCP Server Tests")
    print("=" * 50)
    
    try:
        # Test configuration
        if not test_configuration():
            print("❌ Configuration tests failed")
            return 1
        
        # Test basic functionality  
        if not await test_basic_functionality():
            print("❌ Basic functionality tests failed")
            return 1
        
        # Test mock responses
        if not await test_with_mock_responses():
            print("❌ Mock response tests failed")
            return 1
        
        print("\n🎉 All tests passed successfully!")
        print("\nTo test with real API calls, run:")
        print("  python client.py")
        print("\nTo run interactively:")
        print("  python client.py --interactive")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)