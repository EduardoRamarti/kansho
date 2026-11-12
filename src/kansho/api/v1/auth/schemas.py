

from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    subject: str
    username: str

class UserPublic(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    model_config = ConfigDict(from_attributes=True)

class UserRegister(UserPublic):
    passw: str = Field(min_length=8, max_length=64)
    @classmethod
    def as_form(
        cls, 
        email: Annotated[EmailStr, Form()],
        username: Annotated[str,Form(min_length=3, max_length=30)],
        passw: Annotated[str, Form(min_length=8, max_length=64)]
    ):
        return cls(email=email, username=username, passw=passw)