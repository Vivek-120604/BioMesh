# File: main.py
"""Entrypoint that runs FastAPI in the background and Gradio in the foreground."""
from __future__ import annotations

import threading
import uvicorn
from dotenv import load_dotenv

from app.api import app
from ui import demo


load_dotenv()


def start_api() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
