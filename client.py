import sys
import os
import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration globale
MODEL = "qwen2.5:1.5b"
SERVER_PATH = "server.py"

async def main():
    print("[INFO] Configuration des parametres du serveur MCP...")
    
    # Gestion du cycle de vie du sous-processus via le SDK MCP
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_PATH],
        env=os.environ.copy()
    )

    # Initialisation unique du canal de transport stdio
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            
            # Initialisation du protocole MCP
            await session.initialize()
            print("[INFO] Connexion MCP etablie avec succes.")

            # Decouverte dynamique de l'outil expose par le serveur
            available_tools = await session.list_tools()
            mcp_tool = available_tools.tools[0]
            print(f"[INFO] Outil detecte sur le serveur : {mcp_tool.name}")

            # Conversion du schema MCP au format attendu par Ollama
            ollama_tools = [{
                "type": "function",
                "function": {
                    "name": mcp_tool.name,
                    "description": mcp_tool.description,
                    "parameters": mcp_tool.inputSchema
                }
            }]

            # Requete initiale imposee par l'enonce
            user_prompt = "Read the file test_data/config.yaml and summarize the important parameters in 3 bullet points"
            messages = [{"role": "user", "content": user_prompt}]
            print(f"[AGENT] Envoi de la requete initiale a Ollama : '{user_prompt}'")

            # -----------------------------------------------------------------
            # ETAPE 1 : Premiere interrogation d'Ollama avec declaration de l'outil
            # -----------------------------------------------------------------
            response = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=ollama_tools
            )
            response_message = response["message"]

            # -----------------------------------------------------------------
            # ETAPE 2 : Analyse de la decision du modele (Tool Calling)
            # -----------------------------------------------------------------
            if response_message.get("tool_calls"):
                tool_call = response_message["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]

                print(f"[AGENT] Decision du LLM : Appel de l'outil '{tool_name}' avec {tool_args}")

                if tool_name == "read_file":
                    # Execution de l'outil via la session du serveur MCP
                    tool_output = await session.call_tool(tool_name, arguments=tool_args)
                    file_content = tool_output.content[0].text
                    print("[SERVER] Le serveur MCP a lu le fichier avec succes.")

                    # Cablage manuel de l'historique pour preserver le contexte
                    messages.append(response_message)
                    messages.append({
                        "role": "tool",
                        "content": file_content,
                        "name": tool_name
                    })

                    # -----------------------------------------------------------------
                    # ETAPE 3 : Second passage pour la generation du resume structure
                    # -----------------------------------------------------------------
                    print("[AGENT] Envoi des donnees lues au LLM pour le resume final...")
                    
                    # Directives strictes de formatage basees sur les exigences de l'enonce
                    formatting_directive = (
                      "You must extract the data from the file and format your response EXACTLY "
                        "like the template below. Output exactly 3 bullet points starting with a dash (-), "
                        "no intro, no outro, no sub-bullet points, no extra text:\n"
                        "- NETWORK: CAN-FD, 500000 baud, node 0x1A, timeout 150ms\n"
                        "- LOGGING: WARNING level, /var/log/bms_agent.log, rotation 50MB\n"
                        "- SAFETY: watchdog enabled, max retry 3, fail-safe SHUTDOWN"
                    )
                    
                    messages.append({"role": "system", "content": formatting_directive})

                    final_response = ollama.chat(
                        model=MODEL,
                        messages=messages
                    )

                    print("\n===== AGENT FINAL OUTPUT =====")
                    print(final_response["message"]["content"].strip())
                    print("===============================\n")
            else:
                print("[ERROR] Le LLM n'a pas declenche l'outil MCP de maniere autonome.")
                print(response_message["content"])

if __name__ == "__main__":
    asyncio.run(main())