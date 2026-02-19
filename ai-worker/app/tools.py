import os
import requests

def list_kb_files():
    return os.listdir("data/knowledge_base")

def call_mcp_tool(tool_name, payload):
    response = requests.post(
        "http://mcp-server:9000/tool",
        json={"tool": tool_name, "payload": payload}
    )
    return response.json()

