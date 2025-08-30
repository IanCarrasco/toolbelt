from doctest import debug
from typing import Union
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import json, uvicorn
import sys
import os

# Add the parent directory to the Python path so we can import from lib and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.toolbelt import ToolbeltSession
from models.session_request import SessionRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.environ['OPENAI_TOOLBELT_KEY'])

async def run_toolbelt_session(request: SessionRequest):
    session = ToolbeltSession(client=client)
    async for message in session.run(user_request=request.user_query, session_id=request.session_id):
        yield f"data: {message}\n\n"

@app.post("/start-session")
async def start_session(request: SessionRequest):
    return StreamingResponse(run_toolbelt_session(request), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)