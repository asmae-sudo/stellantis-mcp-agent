# MCP Local AI Agent (Stellantis Summer Internship Exercise)

## Overview

This project implements a **local AI agent** using:

- Model Context Protocol (MCP)
- Ollama local LLM
- Python 3.10+
- stdio transport (no HTTP / no Flask)

The agent is able to:
- Start an MCP server as a subprocess
- Use a tool (`read_file`) to access local files
- Communicate with a local LLM (Ollama)
- Generate a structured summary of configuration files

---

## Architecture

The system is composed of two main components:

### 1. MCP Server (`server.py`)
- Built with `FastMCP` (official MCP SDK)
- Exposes one tool:
  - `read_file(path: str) -> str`
- Reads local files and returns their content

### 2. MCP Client (`client.py`)
- Starts the MCP server
- Connects using `stdio_client`
- Sends a task to the LLM (Ollama)
- Lets the LLM request the tool
- Calls MCP tool (`read_file`)
- Sends file content back to LLM
- Prints final structured summary

---

## Tech Stack

- Python 3.10+
- MCP SDK (official)
- Ollama (qwen2:1.5b or similar)
- anyio / stdio transport
- asyncio

---

## Installation

### 1. Install dependencies
```bash
pip install mcp ollama