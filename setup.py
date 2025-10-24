
from setuptools import setup, find_packages

setup(
    name="ckan-mcp-server",
    version="1.0.0",
    description="MCP Server for CKAN API integration",
    author="MCP CKAN Server",
    packages=find_packages(),
    python_requires=">=3.13",
    install_requires=[
        "mcp>=1.0.0",
        "aiohttp>=3.8.0",
    ],
    entry_points={
        "console_scripts": [
            "ckan-mcp-server=mcp_ckan_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
