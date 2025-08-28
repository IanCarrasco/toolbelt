from pydantic import BaseModel

class SessionRequest(BaseModel):
    user_query: str