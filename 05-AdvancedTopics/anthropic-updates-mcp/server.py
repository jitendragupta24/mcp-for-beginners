#!/usr/bin/env python3
"""
Anthropic Updates MCP Server

This advanced MCP server demonstrates how to automatically pull and integrate
the latest developments from Anthropic. It provides tools to fetch updates,
changelogs, and relevant model improvements from Anthropic's public resources.

This server showcases:
- Integration with GitHub API to fetch repository updates
- Real-time access to Anthropic's development information
- Model information retrieval and aggregation
- Documentation search capabilities
- Release notes and changelog access

For more information about MCP: https://modelcontextprotocol.io/
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_BASE_URL = "https://api.github.com"
DEFAULT_TIMEOUT = 10.0
CACHE_DURATION = timedelta(minutes=5)  # Cache responses for 5 minutes

# Anthropic-related repositories to monitor
ANTHROPIC_REPOS = [
    "anthropics/anthropic-sdk-python",
    "anthropics/anthropic-sdk-typescript",
    "anthropics/anthropic-cookbook",
    "anthropics/courses",
    "modelcontextprotocol/specification",
    "modelcontextprotocol/python-sdk",
    "modelcontextprotocol/typescript-sdk"
]

# Model information (this would typically come from an API)
ANTHROPIC_MODELS = {
    "claude-3-5-sonnet": {
        "name": "Claude 3.5 Sonnet",
        "description": "Most intelligent model for complex reasoning and analysis",
        "max_tokens": 200000,
        "strengths": ["Complex reasoning", "Code generation", "Analysis"],
        "release_date": "2024-06-20"
    },
    "claude-3-opus": {
        "name": "Claude 3 Opus",
        "description": "Most powerful model for highly complex tasks",
        "max_tokens": 200000,
        "strengths": ["Complex reasoning", "Creative writing", "Mathematical analysis"],
        "release_date": "2024-02-29"
    },
    "claude-3-sonnet": {
        "name": "Claude 3 Sonnet",
        "description": "Balanced performance for various tasks",
        "max_tokens": 200000,
        "strengths": ["General tasks", "Analysis", "Content creation"],
        "release_date": "2024-02-29"
    },
    "claude-3-haiku": {
        "name": "Claude 3 Haiku",
        "description": "Fastest model for light tasks",
        "max_tokens": 200000,
        "strengths": ["Speed", "Light tasks", "Quick responses"],
        "release_date": "2024-02-29"
    }
}

@dataclass
class CacheEntry:
    data: Any
    timestamp: datetime

# Simple in-memory cache
cache: Dict[str, CacheEntry] = {}

def get_cache_key(endpoint: str, params: Dict[str, Any]) -> str:
    """Generate a cache key from endpoint and parameters."""
    params_str = json.dumps(params, sort_keys=True)
    return f"{endpoint}:{params_str}"

def is_cache_valid(entry: CacheEntry) -> bool:
    """Check if a cache entry is still valid."""
    return datetime.now() - entry.timestamp < CACHE_DURATION

def get_from_cache(key: str) -> Optional[Any]:
    """Get data from cache if valid."""
    if key in cache:
        entry = cache[key]
        if is_cache_valid(entry):
            return entry.data
        else:
            del cache[key]
    return None

def set_cache(key: str, data: Any) -> None:
    """Store data in cache."""
    cache[key] = CacheEntry(data=data, timestamp=datetime.now())

# Initialize FastMCP server
mcp = FastMCP("AnthropicUpdatesServer")

async def make_github_request(ctx: Context, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Make a request to GitHub API with proper headers and error handling.
    """
    if params is None:
        params = {}
    
    # Check cache first
    cache_key = get_cache_key(endpoint, params)
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        logger.info(f"Returning cached result for {endpoint}")
        return cached_result
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AnthropicUpdatesMCPServer/1.0"
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    url = f"{GITHUB_BASE_URL}/{endpoint.lstrip('/')}"
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            # Cache the result
            set_cache(cache_key, result)
            
            return result
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            error_msg = "GitHub API rate limit exceeded. Consider adding a GITHUB_TOKEN to your .env file."
        else:
            error_msg = f"GitHub API error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except httpx.RequestError as e:
        error_msg = f"Network error when contacting GitHub API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

@mcp.tool()
async def get_latest_updates(ctx: Context, repo: str = "anthropics/anthropic-sdk-python", limit: int = 5) -> str:
    """
    Fetch the latest updates from an Anthropic-related GitHub repository.
    
    Args:
        repo: Repository name (e.g., 'anthropics/anthropic-sdk-python')
        limit: Maximum number of updates to fetch (default: 5)
    """
    if repo not in ANTHROPIC_REPOS:
        return f"Repository '{repo}' is not in the monitored Anthropic repositories. Available repos: {', '.join(ANTHROPIC_REPOS)}"
    
    try:
        # Get latest commits
        commits_data = await make_github_request(ctx, f"repos/{repo}/commits", {"per_page": limit})
        
        # Get latest releases
        releases_data = await make_github_request(ctx, f"repos/{repo}/releases", {"per_page": limit})
        
        updates = {
            "repository": repo,
            "last_updated": datetime.now().isoformat(),
            "latest_commits": [],
            "latest_releases": []
        }
        
        # Process commits
        for commit in commits_data[:limit]:
            updates["latest_commits"].append({
                "sha": commit["sha"][:8],
                "message": commit["commit"]["message"].split('\n')[0],  # First line only
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "url": commit["html_url"]
            })
        
        # Process releases
        for release in releases_data[:limit]:
            updates["latest_releases"].append({
                "tag_name": release["tag_name"],
                "name": release["name"],
                "body": release["body"][:200] + "..." if len(release["body"]) > 200 else release["body"],
                "published_at": release["published_at"],
                "url": release["html_url"]
            })
        
        return json.dumps(updates, indent=2)
        
    except Exception as e:
        return f"Error fetching updates for {repo}: {str(e)}"

@mcp.tool()
async def get_model_info(ctx: Context, model_name: str = "") -> str:
    """
    Retrieve information about Anthropic's AI models.
    
    Args:
        model_name: Specific model to get info for, or empty for all models
    """
    if model_name:
        # Search for exact match or partial match
        for key, model in ANTHROPIC_MODELS.items():
            if model_name.lower() in key.lower() or model_name.lower() in model["name"].lower():
                result = {
                    "model_id": key,
                    **model,
                    "retrieved_at": datetime.now().isoformat()
                }
                return json.dumps(result, indent=2)
        
        return f"Model '{model_name}' not found. Available models: {', '.join(ANTHROPIC_MODELS.keys())}"
    else:
        # Return all models
        result = {
            "models": ANTHROPIC_MODELS,
            "retrieved_at": datetime.now().isoformat(),
            "total_models": len(ANTHROPIC_MODELS)
        }
        return json.dumps(result, indent=2)

@mcp.tool()
async def get_changelog(ctx: Context, repo: str = "anthropics/anthropic-sdk-python", since_days: int = 30) -> str:
    """
    Get changelog information from an Anthropic repository.
    
    Args:
        repo: Repository name to get changelog from
        since_days: Number of days back to look for changes (default: 30)
    """
    if repo not in ANTHROPIC_REPOS:
        return f"Repository '{repo}' is not in the monitored Anthropic repositories. Available repos: {', '.join(ANTHROPIC_REPOS)}"
    
    try:
        since_date = (datetime.now() - timedelta(days=since_days)).isoformat()
        
        # Get commits since the specified date
        commits_data = await make_github_request(
            ctx, 
            f"repos/{repo}/commits",
            {"since": since_date, "per_page": 50}
        )
        
        changelog = {
            "repository": repo,
            "period": f"Last {since_days} days",
            "generated_at": datetime.now().isoformat(),
            "changes": []
        }
        
        for commit in commits_data:
            changelog["changes"].append({
                "date": commit["commit"]["author"]["date"],
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "sha": commit["sha"][:8],
                "url": commit["html_url"]
            })
        
        if not changelog["changes"]:
            changelog["message"] = f"No changes found in the last {since_days} days"
        
        return json.dumps(changelog, indent=2)
        
    except Exception as e:
        return f"Error fetching changelog for {repo}: {str(e)}"

@mcp.tool()
async def search_anthropic_docs(ctx: Context, query: str, limit: int = 5) -> str:
    """
    Search through Anthropic's documentation and resources.
    
    Args:
        query: Search term to look for
        limit: Maximum number of results to return (default: 5)
    """
    try:
        # Search across multiple Anthropic repositories for documentation
        search_results = {
            "query": query,
            "searched_at": datetime.now().isoformat(),
            "results": []
        }
        
        # Search in cookbook repository (contains many examples and docs)
        search_data = await make_github_request(
            ctx,
            "search/code",
            {
                "q": f"{query} repo:anthropics/anthropic-cookbook",
                "per_page": limit
            }
        )
        
        for item in search_data.get("items", [])[:limit]:
            search_results["results"].append({
                "repository": item["repository"]["full_name"],
                "file_path": item["path"],
                "file_name": item["name"],
                "url": item["html_url"],
                "score": item["score"]
            })
        
        # Also search in courses repository
        courses_search = await make_github_request(
            ctx,
            "search/code",
            {
                "q": f"{query} repo:anthropics/courses",
                "per_page": limit
            }
        )
        
        for item in courses_search.get("items", [])[:limit]:
            search_results["results"].append({
                "repository": item["repository"]["full_name"],
                "file_path": item["path"],
                "file_name": item["name"],
                "url": item["html_url"],
                "score": item["score"]
            })
        
        # Sort by score and limit results
        search_results["results"] = sorted(
            search_results["results"], 
            key=lambda x: x["score"], 
            reverse=True
        )[:limit]
        
        search_results["total_found"] = len(search_results["results"])
        
        return json.dumps(search_results, indent=2)
        
    except Exception as e:
        return f"Error searching Anthropic documentation: {str(e)}"

@mcp.tool()
async def get_release_notes(ctx: Context, repo: str = "anthropics/anthropic-sdk-python", version: str = "") -> str:
    """
    Fetch release notes for specific versions from Anthropic repositories.
    
    Args:
        repo: Repository name to get release notes from
        version: Specific version to get notes for, or empty for latest
    """
    if repo not in ANTHROPIC_REPOS:
        return f"Repository '{repo}' is not in the monitored Anthropic repositories. Available repos: {', '.join(ANTHROPIC_REPOS)}"
    
    try:
        if version:
            # Get specific release
            release_data = await make_github_request(ctx, f"repos/{repo}/releases/tags/{version}")
            
            release_notes = {
                "repository": repo,
                "version": version,
                "release": {
                    "tag_name": release_data["tag_name"],
                    "name": release_data["name"],
                    "body": release_data["body"],
                    "published_at": release_data["published_at"],
                    "author": release_data["author"]["login"],
                    "url": release_data["html_url"],
                    "prerelease": release_data["prerelease"],
                    "draft": release_data["draft"]
                }
            }
        else:
            # Get latest release
            release_data = await make_github_request(ctx, f"repos/{repo}/releases/latest")
            
            release_notes = {
                "repository": repo,
                "latest_release": {
                    "tag_name": release_data["tag_name"],
                    "name": release_data["name"],
                    "body": release_data["body"],
                    "published_at": release_data["published_at"],
                    "author": release_data["author"]["login"],
                    "url": release_data["html_url"],
                    "prerelease": release_data["prerelease"],
                    "draft": release_data["draft"]
                }
            }
        
        release_notes["retrieved_at"] = datetime.now().isoformat()
        
        return json.dumps(release_notes, indent=2)
        
    except Exception as e:
        return f"Error fetching release notes for {repo}: {str(e)}"

@mcp.tool()
async def get_repository_stats(ctx: Context, repo: str = "anthropics/anthropic-sdk-python") -> str:
    """
    Get statistics and information about an Anthropic repository.
    
    Args:
        repo: Repository name to get statistics for
    """
    if repo not in ANTHROPIC_REPOS:
        return f"Repository '{repo}' is not in the monitored Anthropic repositories. Available repos: {', '.join(ANTHROPIC_REPOS)}"
    
    try:
        # Get repository information
        repo_data = await make_github_request(ctx, f"repos/{repo}")
        
        # Get recent activity
        commits_data = await make_github_request(ctx, f"repos/{repo}/commits", {"per_page": 10})
        
        stats = {
            "repository": repo,
            "name": repo_data["name"],
            "description": repo_data["description"],
            "language": repo_data["language"],
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "open_issues": repo_data["open_issues_count"],
            "created_at": repo_data["created_at"],
            "updated_at": repo_data["updated_at"],
            "pushed_at": repo_data["pushed_at"],
            "size_kb": repo_data["size"],
            "default_branch": repo_data["default_branch"],
            "topics": repo_data["topics"],
            "license": repo_data["license"]["name"] if repo_data["license"] else None,
            "url": repo_data["html_url"],
            "recent_activity": {
                "commits_last_10": len(commits_data),
                "last_commit_date": commits_data[0]["commit"]["author"]["date"] if commits_data else None
            },
            "retrieved_at": datetime.now().isoformat()
        }
        
        return json.dumps(stats, indent=2)
        
    except Exception as e:
        return f"Error fetching repository stats for {repo}: {str(e)}"

@mcp.tool()
async def list_monitored_repos(ctx: Context) -> str:
    """
    List all Anthropic repositories that this server monitors.
    """
    result = {
        "monitored_repositories": ANTHROPIC_REPOS,
        "total_count": len(ANTHROPIC_REPOS),
        "description": "These are the Anthropic-related repositories monitored by this MCP server",
        "last_updated": datetime.now().isoformat()
    }
    
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    logger.info("Starting Anthropic Updates MCP Server...")
    logger.info(f"Monitoring {len(ANTHROPIC_REPOS)} repositories")
    logger.info(f"GitHub token configured: {'Yes' if GITHUB_TOKEN else 'No (rate limits may apply)'}")
    
    # Run the server
    mcp.run()