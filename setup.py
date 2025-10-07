#!/usr/bin/env python3
"""
Setup script for Historical Facts MCP Server
"""

from setuptools import setup, find_packages

setup(
    name="historical-facts-mcp-server",
    version="1.0.0",
    description="A fun MCP server that provides historical facts from events that happened on the same date in history",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="romantic_franklin",
    author_email="romantic_franklin@fern.ai",
    url="https://github.com/oscar-fern-labs/historical-facts-mcp-server",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.16.0",
        "httpx>=0.28.0",
        "python-dateutil>=2.9.0"
    ],
    entry_points={
        "console_scripts": [
            "historical-facts-mcp=historical_facts_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="mcp, historical-facts, wikipedia, chatgpt, claude, ai",
)
