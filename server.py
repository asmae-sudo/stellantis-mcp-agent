from mcp.server.fastmcp import FastMCP
import os

server = FastMCP("file-server")

@server.tool()
def read_file(path: str) -> str:
    if not os.path.exists(path):
        return "ERROR: file not found"

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    server.run()