from pydantic import BaseModel


class GuestJoinRequest(BaseModel):
    trip_id: str
    join_code: str
    nickname: str


class GuestTokenResponse(BaseModel):
    access_token: str
    token_type: str = "guest"
    trip_id: str
    nickname: str
