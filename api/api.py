from doctest import debug
from typing import Union
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import supabase
import json, uvicorn
from dotenv import load_dotenv
import sys
import os

# Add the parent directory to the Python path so we can import from lib and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.toolbelt import ToolbeltSession, supabase_client
from models.session_request import SessionRequest

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.local'))
supabase_client = supabase.Client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY"))

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
    all_messages = []
    
    async for message in session.run(user_request=request.user_query, session_id=request.session_id, user_id=request.user_id):
        all_messages.append(message)
        yield f"data: {message}\n\n"
    
    supabase_client.table("sessions").update({
        "session_log": all_messages
    }).eq("id", request.session_id).execute()

@app.post("/start-session")
async def start_session(request: SessionRequest):
    supabase_client.table("sessions").update({
        "current_query": request.user_query
    }).eq("id", request.session_id).execute()
    # Read the user from the user_id in the request
    user_id = request.user_id
    user_response = supabase_client.table("special_access").select("*").eq("id", user_id).single().execute()
    if user_response.data['access'] is not 'FREE':
        return StreamingResponse(run_toolbelt_session(request), media_type="text/event-stream")
    else:
        return StreamingResponse(run_toolbelt_session(request), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)