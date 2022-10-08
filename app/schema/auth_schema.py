from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=15)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=4, max_length=20)


class AuthResponse(BaseModel):
    msg: str
    user: dict
    token: str


class SigninRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=15)
    password: str = Field(..., min_length=4, max_length=20)
