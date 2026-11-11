

from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    subject: str
    username: str

class UserPublic(BaseModel):
    email: str
    username: str
    model_config = ConfigDict(from_attributes=True)

class UserRegister(UserPublic):
    passw: str
    @classmethod
    def as_form(
        cls, 
        email: Annotated[str, Form(min_length=3)],
        username: Annotated[str,Form(min_length=3)],
        passw: Annotated[str, Form(min_length=8)]
    ):
        return cls(email=email, username=username, passw=passw)