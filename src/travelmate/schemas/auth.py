from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str = Field(min_length=8, description="Password must be at least 8 characters")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str = ""
    token_type: str = "bearer"
    user_id: str
    name: str


class RefreshRequest(BaseModel):
    refresh_token: str
