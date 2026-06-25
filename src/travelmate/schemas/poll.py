from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PollOptionCreate(BaseModel):
    label: str


class PollCreate(BaseModel):
    question: str
    options: list[str]  # min 2 options


class PollVoteRequest(BaseModel):
    option_id: str


class PollOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    label: str
    vote_count: int = 0
    voted: bool = False


class PollResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    creator_id: str
    creator_name: str = ""
    question: str
    is_closed: bool
    options: list[PollOptionResponse] = []
    total_votes: int = 0
    created_at: datetime | None = None
