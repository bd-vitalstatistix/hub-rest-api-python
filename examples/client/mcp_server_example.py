#!/usr/bin/env python
"""
Example: Using BlackDuck MCP Server

This example demonstrates how to use the BlackDuck MCP (Model Context Protocol)
server to interact with BlackDuck Hub through AI assistants like Claude.

The MCP server provides 6 core tools for programmatic access to BlackDuck data:
- list_projects: List all BlackDuck projects
- get_project_details: Get detailed information about a specific project
- list_project_versions: List versions for a specific project
- search_projects: Search for projects by name
- get_project_vulnerabilities: Get security vulnerabilities for a project version
- list_project_components: List components in a project version

Requirements:
    pip install blackduck[mcp]

Environment Variables:
    BLACKDUCK_URL: Your BlackDuck server URL (e.g., https://your.blackduck.url)
    BLACKDUCK_TOKEN: Your BlackDuck API token

Usage:

1. Set environment variables:
    export BLACKDUCK_URL="https://your.blackduck.url"
    export BLACKDUCK_TOKEN="your-api-token"

2. Start the MCP server:
    blackduck --mcp

3. Configure your MCP client (e.g., Claude Code):
    Add to your MCP configuration file:
    {
      "mcpServers": {
        "blackduck": {
          "command": "blackduck",
          "args": ["--mcp"],
          "env": {
            "BLACKDUCK_URL": "https://your.blackduck.url",
            "BLACKDUCK_TOKEN": "your-api-token"
          }
        }
      }
    }

4. Interact with BlackDuck through your AI assistant:
    - "List all my BlackDuck projects"
    - "Show me details for project XYZ"
    - "What are the vulnerabilities in project ABC version 1.0?"
    - "Search for projects containing 'web-app'"
    - "List components in my latest project version"

Example MCP Client Interactions:
"""

import os
import sys


def print_example_queries():
    """Print example queries that can be used with the MCP server"""

    examples = [
        {
            "description": "List all projects",
            "tool": "list_projects",
            "query": "Show me all BlackDuck projects",
            "parameters": {"limit": 10}
        },
        {
            "description": "Get project details",
            "tool": "get_project_details",
            "query": "What are the details of the 'my-web-app' project?",
            "parameters": {"project_name": "my-web-app"}
        },
        {
            "description": "List project versions",
            "tool": "list_project_versions",
            "query": "List all versions of the 'my-web-app' project",
            "parameters": {"project_name": "my-web-app", "limit": 20}
        },
        {
            "description": "Search for projects",
            "tool": "search_projects",
            "query": "Find all projects with 'api' in the name",
            "parameters": {"query": "api", "limit": 25}
        },
        {
            "description": "Get vulnerabilities (latest version)",
            "tool": "get_project_vulnerabilities",
            "query": "What vulnerabilities are in the latest version of 'my-web-app'?",
            "parameters": {"project_name": "my-web-app", "limit": 50}
        },
        {
            "description": "Get vulnerabilities (specific version)",
            "tool": "get_project_vulnerabilities",
            "query": "Show HIGH severity vulnerabilities in version 2.0 of 'my-web-app'",
            "parameters": {
                "project_name": "my-web-app",
                "version_name": "2.0",
                "limit": 50
            }
        },
        {
            "description": "List components",
            "tool": "list_project_components",
            "query": "What components are in the latest version of 'my-web-app'?",
            "parameters": {"project_name": "my-web-app", "limit": 50}
        }
    ]

    print("=" * 80)
    print("BlackDuck MCP Server - Example Queries")
    print("=" * 80)
    print()

    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}")
        print(f"   Tool: {example['tool']}")
        print(f"   Natural Language Query: \"{example['query']}\"")
        print(f"   Parameters: {example['parameters']}")
        print()

    print("=" * 80)
    print()


def check_environment():
    """Check if required environment variables are set"""

    url = os.environ.get('BLACKDUCK_URL')
    token = os.environ.get('BLACKDUCK_TOKEN')

    if not url or not token:
        print("ERROR: Missing required environment variables")
        print()
        print("Please set the following environment variables:")
        print("  BLACKDUCK_URL=https://your.blackduck.url")
        print("  BLACKDUCK_TOKEN=your-api-token")
        print()
        return False

    print(f"✓ BLACKDUCK_URL: {url}")
    print(f"✓ BLACKDUCK_TOKEN: {'*' * (len(token) - 4) + token[-4:]}")
    print()
    return True


def print_usage():
    """Print usage instructions"""

    print("BlackDuck MCP Server Example")
    print()
    print("This example shows how to use the BlackDuck MCP server with AI assistants.")
    print()
    print("Steps:")
    print("  1. Install: pip install blackduck[mcp]")
    print("  2. Set environment variables (see above)")
    print("  3. Start server: blackduck --mcp")
    print("  4. Configure your MCP client")
    print("  5. Interact with BlackDuck through natural language")
    print()


def main():
    """Main entry point"""

    print()
    print_usage()

    if not check_environment():
        print("Please configure environment variables and try again.")
        print()
        sys.exit(1)

    print_example_queries()

    print("MCP Server Ready!")
    print()
    print("To start the MCP server, run:")
    print("  blackduck --mcp")
    print()
    print("Then use your MCP client (e.g., Claude Code) to interact with BlackDuck")
    print("using the example queries shown above.")
    print()


if __name__ == '__main__':
    main()
