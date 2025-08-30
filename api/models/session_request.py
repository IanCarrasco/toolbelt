from pydantic import BaseModel

class SessionRequest(BaseModel):
    user_query: str
    session_id: str
    user_id: str