from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import IntegrityError
from pwdlib import PasswordHash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from kansho.core.db import get_db
from kansho.core.security import create_access_token, get_current_user

from .repository import AuthRepository
from .schemas import Token, UserPublic, UserRegister

FAKE_USERS = {
    "faker@example.com": {"email": "fake@example.com", "username": "faker", "password": "secret123"},
    "alumno@example.com":  {"email": "alumno@example.com",  "username": "alumno",  "password": "123456"},
}


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/sign-up", response_model=UserPublic, status_code=201)
async def signup(user: Annotated[UserRegister, Depends(UserRegister.as_form)], db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    if repo.search_user(username=user.username, email=user.email):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Conflict")
    try: 
        hasher = PasswordHash.recommended()
        hashed_passw = hasher.hash(user.passw)
        new_user = repo.create_new_user(
            username=user.username,
            email=user.email,
            passw=hashed_passw
        )
        return new_user
    except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Conflict")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating User")

@router.post("/login", response_model=Token)
# OAuth2PasswordRequestForm → lee el usuario y la contraseña que vienen en el formulario de la petición y entrégamelos en un objeto
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS.get(form_data.username)
    if not user or user['password'] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    token = create_access_token(
        data={"sub": user["email"], "username": user["username"]},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserPublic)
async def read_me(current = Depends(get_current_user)):
    return {"email": current["email"], "username": current["username"]}
