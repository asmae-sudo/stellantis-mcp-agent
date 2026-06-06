import subprocess
import sys
import time
import asyncio
import ollama
import re

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

MODEL = "qwen2:1.5b"
SERVER_PATH = "server.py"


# -----------------------
# START MCP SERVER
# -----------------------
def start_server():
    print("[INFO] Starting MCP server...")

    return subprocess.Popen(
        [sys.executable, SERVER_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# -----------------------
# CALL LLM
# -----------------------
def call_llm(prompt):
    res = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return res["message"]["content"]


# -----------------------
# PARSE TOOL REQUEST (SAFE)
# -----------------------
def parse_tool(text):
    if "read_file" not in text:
        return None, None

    match = re.search(r"PATH\s*[:=]\s*(.+)", text)
    path = match.group(1).strip() if match else "test_data/config.yaml"

    return "read_file", path


# -----------------------
# CLEAN BULLETS (STRICT 3)
# -----------------------
def format_bullets(text):
    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if line.startswith("-"):
            lines.append(line)

    # keep only 3
    lines = lines[:3]

    categories = ["NETWORK", "LOGGING", "SAFETY"]

    while len(lines) < 3:
        lines.append(f"- {categories[len(lines)]}: missing")

    return lines


# -----------------------
# MAIN
# -----------------------
async def main():

    server = start_server()
    time.sleep(2)

    print("\n[INFO] Connecting MCP client...\n")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_PATH],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await session.list_tools()
            print("[INFO] Available tools:", [t.name for t in tools.tools])

            # -----------------------
            # STEP 1: TOOL DECISION
            # -----------------------
            prompt = """
You are a strict MCP agent.

You MUST output ONLY:

TOOL: read_file
PATH: test_data/config.yaml

No explanation.
No markdown.
No extra text.
"""

            llm_response = call_llm(prompt)
            print("\n[LLM OUTPUT]\n", llm_response)

            tool, path = parse_tool(llm_response)

            if tool != "read_file":
                print("[ERROR] Tool not requested correctly")
                return

            # -----------------------
            # STEP 2: CALL MCP TOOL (REAL)
            # -----------------------
            print("\n[INFO] Calling MCP tool...\n")

            result = await session.call_tool(
                "read_file",
                {"path": path}
            )

            file_content = result.content[0].text

            print("[INFO] File loaded")

            # -----------------------
            # STEP 3: FINAL SUMMARY
            # -----------------------
            final_prompt = f"""
You are a strict system engineer.

Summarize the configuration into EXACTLY 3 bullet points.

FORMAT (must follow exactly):

- NETWORK: include protocol, baudrate, node id, timeout
- LOGGING: include level, output path, rotation size
- SAFETY: include watchdog status, max retry, fail-safe mode

RULES:
- Exactly 3 bullets
- Must include numeric values when available
- No extra text
- No explanations
- No missing fields allowed


CONTENT:
{file_content}
"""

            final = call_llm(final_prompt)

            bullets = format_bullets(final)

            print("\n===== FINAL ANSWER =====\n")
            print("\n".join(bullets))

            server.terminate()


if __name__ == "__main__":
    asyncio.run(main())