
# CKAN MCP Server

A Model Context Protocol (MCP) server for the CKAN API that enables browsing and managing CKAN data portals through MCP-compatible clients.

## What is this?

This is an MCP server that provides access to CKAN (Comprehensive Knowledge Archive Network) APIs through the Model Context Protocol. It can be used with MCP-compatible clients like Claude Desktop, IDEs, or other AI applications to interact with CKAN data portals.

## Requirements

- Python 3.13 or higher
- pip (Python package installer)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

- `CKAN_URL`: The base URL of your CKAN portal (e.g. `https://demo.ckan.org`)
- `CKAN_API_KEY`: (Optional) Your CKAN API key for write operations

Example:
```bash
export CKAN_URL="https://demo.ckan.org"
export CKAN_API_KEY="your-api-key-here"
```

You can also copy `.env.example` to `.env` and set your configuration there.

## Usage

### Running the server directly
```bash
python mcp_ckan_server.py
```

### Using Docker
```bash
# Build the image
docker build -t ckan-mcp-server .

# Run with environment variables
docker run -e CKAN_URL="https://demo.ckan.org" -e CKAN_API_KEY="your-key" ckan-mcp-server
```

### Using Docker Compose
```bash
# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run the server
docker-compose up
```

## Available Tools

The MCP server provides the following tools:

### Packages/Datasets
- `ckan_package_list`: List all packages
- `ckan_package_show`: Show details of a specific package
- `ckan_package_search`: Search for packages

### Organizations
- `ckan_organization_list`: List all organizations
- `ckan_organization_show`: Show organization details

### DataStore
- `ckan_datastore_search` Search DataStore Tables by Resource

### Groups and Tags
- `ckan_group_list`: List all groups
- `ckan_tag_list`: List all tags

### Resources
- `ckan_resource_show`: Show resource details

### System
- `ckan_site_read`: Site information
- `ckan_status_show`: Status and version information

## Examples

### Search packages
```json
{
  "tool": "ckan_package_search",
  "arguments": {
    "q": "climate data",
    "rows": 5,
    "sort": "score desc"
  }
}
```

### Show organization
```json
{
  "tool": "ckan_organization_show",
  "arguments": {
    "id": "sample-organization",
    "include_datasets": true
  }
}
```

### List all tags
```json
{
  "tool": "ckan_tag_list",
  "arguments": {}
}
```

## Resources

The server also provides the following resources:
- `ckan://api/docs`: API documentation
- `ckan://config`: Server configuration

## Using with MCP Clients

### Claude Desktop

Add this to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "ckan": {
      "command": "python",
      "args": ["/path/to/mcp_ckan_server.py"],
      "env": {
        "CKAN_URL": "https://demo.ckan.org",
        "CKAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Other MCP Clients

The server communicates via stdio, so any MCP-compatible client can connect to it by running the Python script and communicating through standard input/output.

## CKAN API Reference

This MCP server implements the main endpoints of the CKAN API v3. 
Complete documentation: https://docs.ckan.org/en/latest/api/

## License

Mozilla Public License Version 2.0

## Author

(C) 2025, Ondics GmbH, https://ondics.de
