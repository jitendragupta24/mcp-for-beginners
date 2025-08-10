# Anthropic Updates MCP Server

This advanced MCP server demonstrates how to automatically pull and integrate the latest developments from Anthropic. The server provides tools to fetch updates, changelogs, and relevant model improvements from Anthropic's public resources.

## Features

The server implements several tools to access Anthropic development information:

- `get_latest_updates`: Fetch the latest updates from Anthropic's GitHub repositories
- `get_model_info`: Retrieve information about Anthropic's AI models
- `get_changelog`: Get changelog information from Anthropic repositories
- `search_anthropic_docs`: Search through Anthropic's documentation
- `get_release_notes`: Fetch release notes for specific versions

## Prerequisites

- Python 3.8+
- Required Python packages (install via `pip install -r requirements.txt`):
  - `mcp`
  - `httpx`
  - `python-dotenv`
  - `pydantic`

## Setup

1. Clone this repository
2. Navigate to this directory: `cd 05-AdvancedTopics/anthropic-updates-mcp/`
3. Install dependencies: `pip install -r requirements.txt`
4. (Optional) Create a `.env` file with GitHub token for higher API rate limits:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

## Running the Server

```bash
python server.py
```

## Usage Examples

The server provides several tools that can be used by MCP clients:

### Get Latest Updates
```python
# This tool fetches the latest commits and releases from Anthropic repositories
result = await client.call_tool("get_latest_updates", {
    "repo": "anthropics/anthropic-sdk-python",
    "limit": 5
})
```

### Get Model Information
```python
# Fetch information about Anthropic's models
result = await client.call_tool("get_model_info", {
    "model_name": "claude-3"
})
```

### Search Documentation
```python
# Search through Anthropic's documentation
result = await client.call_tool("search_anthropic_docs", {
    "query": "function calling",
    "limit": 3
})
```

## Architecture

This MCP server demonstrates several advanced patterns:

1. **External API Integration**: Shows how to integrate with GitHub API and other external services
2. **Error Handling**: Robust error handling for network requests and API limitations
3. **Rate Limiting**: Proper handling of API rate limits
4. **Caching**: Basic caching mechanisms to avoid redundant requests
5. **Configuration Management**: Environment-based configuration

## Educational Value

This example teaches:

- How to integrate external APIs into MCP servers
- Best practices for handling HTTP requests in MCP tools
- Error handling and resilience patterns
- Working with GitHub API and documentation sources
- Real-world application of MCP for information aggregation

## Extending the Server

You can extend this server by:

- Adding more Anthropic repositories to monitor
- Implementing webhook notifications for updates
- Adding filtering and search capabilities
- Integrating with other AI model providers
- Adding support for different output formats

## Security Considerations

- The server uses read-only access to public repositories
- GitHub tokens are optional but recommended for higher rate limits
- All external requests are properly validated and sanitized
- No sensitive information is stored or transmitted

## Troubleshooting

**Rate Limiting**: If you encounter rate limiting errors, add a GitHub token to your `.env` file.

**Network Errors**: Ensure you have a stable internet connection. The server includes retry logic for transient failures.

**Missing Dependencies**: Run `pip install -r requirements.txt` to ensure all dependencies are installed.

## Contributing

This is an educational example. Feel free to modify and extend it for your learning purposes.