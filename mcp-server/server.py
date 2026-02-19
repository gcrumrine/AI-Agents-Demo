from fastapi import FastAPI
import platform
import psutil

app = FastAPI()

@app.post("/tool")
def run_tool(request: dict):
    tool = request.get("tool")

    if tool == "system_info":
        return {
            "platform": platform.system(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent
        }

    return {"error": "unknown tool"}

