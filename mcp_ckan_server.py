
#!/usr/bin/env python3

import asyncio

import json
import logging
import os
import pprint
import ssl
import certifi
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin
import aiohttp
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from dotenv import load_dotenv


load_dotenv()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
# Configure logging
logging.basicConfig(level=logging.INFO,filename="mcp-ckan-server.log")
logger = logging.getLogger("mcp-ckan-server")

class CKANAPIClient:
    """CKAN API client for making HTTP requests"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MCP-CKAN-Server/1.0'
        }
        if self.api_key:
            headers['Authorization'] = self.api_key
        return headers
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to CKAN API"""
        url = urljoin(f"{self.base_url}/api/3/action/", endpoint)
        headers = self._get_headers()
        
        try:
            
            async with self.session.request(method, url, headers=headers, json=data) as response:
                result = await response.json()
                logger.warn(result)
                if not result.get('success', False):
                    error_msg = result.get('error', {})
                    raise Exception(f"CKAN API Error: {error_msg}")
                
                return result.get('result', {})
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

# Global CKAN client
ckan_client = None

# Initialize MCP server
server = Server("ckan-mcp-server")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available CKAN API tools"""
    return [
        types.Tool(
            name="ckan_package_list",
            description="Get list of all packages (datasets) in CKAN (unsorted)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of packages to return",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer", 
                        "description": "Offset for pagination",
                        "default": 0
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_package_show",
            description="Get details of a specific package/dataset (like dates)",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Package ID or name"
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="ckan_package_search",
            description="Search for packages using queries",
            inputSchema={
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Search query",
                        "default": "*:*"
                    },
                    "fq": {
                        "type": "string",
                        "description": "Filter query"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort field and direction (e.g., 'score desc')"
                    },
                    "rows": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    },
                    "start": {
                        "type": "integer",
                        "description": "Offset for pagination",
                        "default": 0
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_organization_list",
            description="Get list of all organizations",
            inputSchema={
                "type": "object",
                "properties": {
                    "all_fields": {
                        "type": "boolean",
                        "description": "Include all organization fields",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_organization_show",
            description="Get details of a specific organization",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Organization ID or name"
                    },
                    "include_datasets": {
                        "type": "boolean",
                        "description": "Include organization's datasets",
                        "default": False
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="ckan_group_list",
            description="Get list of all groups",
            inputSchema={
                "type": "object",
                "properties": {
                    "all_fields": {
                        "type": "boolean",
                        "description": "Include all group fields",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_tag_list",
            description="Get list of all tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "vocabulary_id": {
                        "type": "string",
                        "description": "Vocabulary ID to filter tags"
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_resource_show",
            description="Get details of a specific resource",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Resource ID"
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="ckan_site_read",
            description="Get site information and statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="ckan_status_show",
            description="Get CKAN site status and version information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        types.Tool(
            name="ckan_datastore_search",
            description="Search records in a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of the resource to search"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip"
                    },
                    "q": {
                        "type": "string",
                        "description": "Query string in CKAN search syntax"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order e.g. 'field asc'"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return in results"
                    }
                },
                "required": ["resource_id"]
            }
        ),
        # @TODO Untested
        # types.Tool(
        #     name="ckan_datastore_create",
        #     description="Create an empty dataset in the datastore",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to create"
        #             },
        #             "table_name": {
        #                 "type": "string",
        #                 "description": "Optional table name"
        #             },
        #             "schema": {
        #                 "type": "object",
        #                 "description": "Schema definition for the dataset"
        #             }
        #         },
        #         "required": ["resource_id"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_upsert",
        #     description="Insert or update rows in a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to upsert"
        #             },
        #             "records": {
        #                 "type": "array",
        #                 "items": {"type": "object","properties": {}},
        #                 "description": "List of records to upsert"
        #             },
        #             "method": {
        #                 "type": "string",
        #                 "enum": ["insert", "update", "upsert"],
        #                 "description": "Method to use"
        #             }
        #         },
        #         "required": ["resource_id", "records", "method"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_delete",
        #     description="Delete rows from a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to delete from"
        #             },
        #             "ids": {
        #                 "type": "array",
        #                 "items": {"type": "string"},
        #                 "description": "List of record IDs to delete"
        #             }
        #         },
        #         "required": ["resource_id", "ids"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_commit",
        #     description="Commit changes to a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to commit"
        #             }
        #         },
        #         "required": ["resource_id"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_table_create",
        #     description="Create a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource"
        #             },
        #             "schema": {
        #                 "type": "object",
        #                 "description": "Schema definition"
        #             }
        #         },
        #         "required": ["resource_id", "schema"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_table_delete",
        #     description="Delete a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to delete"
        #             }
        #         },
        #         "required": ["resource_id"]
        #     }
        # ),
        
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
    """Handle tool calls to CKAN API"""
    if not ckan_client:
        raise Exception("CKAN client not initialized. Please set CKAN_URL environment variable.")
    
    try:
        if name == "ckan_package_list":
            limit = arguments.get("limit", 100) if arguments else 100
            offset = arguments.get("offset", 0) if arguments else 0
            result = await ckan_client._make_request("GET", f"package_list?limit={limit}&offset={offset}")
            
        elif name == "ckan_package_show":
            package_id = arguments["id"]
            result = await ckan_client._make_request("GET", f"package_show?id={package_id}")
            
        elif name == "ckan_package_search":
            params = arguments or {}
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            query_string = "&".join(query_params)
            result = await ckan_client._make_request("GET", f"package_search?{query_string}")
            
        elif name == "ckan_organization_list":
            all_fields = arguments.get("all_fields", False) if arguments else False
            result = await ckan_client._make_request("GET", f"organization_list?all_fields={all_fields}")
            
        elif name == "ckan_organization_show":
            org_id = arguments["id"]
            include_datasets = arguments.get("include_datasets", False)
            result = await ckan_client._make_request("GET", f"organization_show?id={org_id}&include_datasets={include_datasets}")
            
        elif name == "ckan_group_list":
            all_fields = arguments.get("all_fields", False) if arguments else False
            result = await ckan_client._make_request("GET", f"group_list?all_fields={all_fields}")
            
        elif name == "ckan_tag_list":
            params = arguments or {}
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            query_string = "&".join(query_params)
            endpoint = f"tag_list?{query_string}" if query_string else "tag_list"
            result = await ckan_client._make_request("GET", endpoint)
            
        elif name == "ckan_resource_show":
            resource_id = arguments["id"]
            result = await ckan_client._make_request("GET", f"resource_show?id={resource_id}")
            
        elif name == "ckan_site_read":
            result = await ckan_client._make_request("GET", "site_read")
            
        elif name == "ckan_status_show":
            result = await ckan_client._make_request("GET", "status_show")

        elif name == "ckan_datastore_search":
            result = await ckan_client._make_request("POST", "datastore_search", data=arguments)
        # @TODO: untested
        # elif name == "ckan_datastore_create":
        #     result = await ckan_client._make_request("POST", "datastore_create", data=arguments)
        # elif name == "ckan_datastore_update":
        #     result = await ckan_client._make_request("POST", "datastore_update", data=arguments)
        # elif name == "ckan_datastore_upsert":
        #     result = await ckan_client._make_request("POST", "datastore_upsert", data=arguments)
        # elif name == "ckan_datastore_delete":
        #     result = await ckan_client._make_request("POST", "datastore_delete", data=arguments)
        
            
        else:
            raise Exception(f"Unknown tool: {name}")
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]
        
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [
            types.TextContent(
                type="text", 
                text=f"Error: {str(e)}"
            )
        ]

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available CKAN resources"""
    return [
        types.Resource(
            uri="ckan://api/docs",
            name="CKAN API Documentation",
            description="Official CKAN API documentation and endpoints",
            mimeType="text/plain"
        ),
        types.Resource(
            uri="ckan://config",
            name="CKAN Server Configuration",
            description="Current CKAN server configuration and connection details",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read CKAN resources"""
    if uri == "ckan://api/docs":
        return """
CKAN API Documentation Summary

Base URL: Configure via CKAN_URL environment variable
API Version: 3

Key Endpoints:
- package_list: Get all packages/datasets
- package_show: Get package details
- package_search: Search packages
- organization_list: Get all organizations  
- organization_show: Get organization details
- group_list: Get all groups
- tag_list: Get all tags
- resource_show: Get resource details
- site_read: Get site information
- status_show: Get site status

Authentication: Set CKAN_API_KEY environment variable for write operations

Full documentation: https://docs.ckan.org/en/latest/api/
        """
    elif uri == "ckan://config":
        config = {
            "base_url": ckan_client.base_url if ckan_client else "Not configured",
            "api_key_configured": bool(ckan_client and ckan_client.api_key),
            "session_active": bool(ckan_client and ckan_client.session)
        }
        return json.dumps(config, indent=2)
    else:
        raise Exception(f"Unknown resource: {uri}")

async def main():
    """Main server function"""
    import os
    
    # Initialize CKAN client
    ckan_url = os.getenv("CKAN_URL")
    if not ckan_url:
        logger.error("CKAN_URL environment variable not set")
        raise Exception("CKAN_URL environment variable is required")
    
    ckan_api_key = os.getenv("CKAN_API_KEY")
    
    global ckan_client
    ckan_client = CKANAPIClient(ckan_url, ckan_api_key)
    
    # Start the CKAN client session
    await ckan_client.__aenter__()
    
    try:
        # Run the MCP server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ckan-mcp-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        # Clean up CKAN client
        await ckan_client.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(main())
