import os
from mcp.server.fastmcp import FastMCP

# Initialisation du serveur MCP
mcp = FastMCP("Stellantis-BMS-Server")

@mcp.tool()
def read_file(path: str) -> str:
    """
    Read the contents of a local file safely and return its text content.
    
    Args:
        path (str): The relative path to the file.
    """
    try:
        # Résolution du chemin absolu pour éviter les erreurs d'exécution
        absolute_path = os.path.abspath(path)
        
        if not os.path.exists(absolute_path):
            return f"Error: The file at '{path}' does not exist."
            
        if not os.path.isfile(absolute_path):
            return f"Error: '{path}' is a directory, not a file."
            
        with open(absolute_path, "r", encoding="utf-8") as f:
            return f.read()
            
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    # Forcer explicitement le transport stdio comme imposé par la stack Stellantis
    mcp.run(transport="stdio")