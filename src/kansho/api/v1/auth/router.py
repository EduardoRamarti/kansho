from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import IntegrityError
from pwdlib import PasswordHash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from kansho.core.db import get_db
from kansho.core.security import DUMMY_PH, create_access_token, get_current_user

from .repository import AuthRepository
from .schemas import Token, UserPublic, UserPublicInfo, UserRegister

FAKE_USERS = {
    "faker@example.com": {"email": "fake@example.com", "username": "faker", "password": "secret123"},
    "alumno@example.com":  {"email": "alumno@example.com",  "username": "alumno",  "password": "123456"},
}


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/sign-up", response_model=UserPublic, status_code=201)
async def signup(user: Annotated[UserRegister, Depends(UserRegister.as_form)], db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    hasher = PasswordHash.recommended()
    if repo.search_user_register(username=user.username, email=user.email):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Conflict")
    try: 
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
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # user = FAKE_USERS.get(form_data.username)
    repo = AuthRepository(db)
    hasher = PasswordHash.recommended()
    user = repo.search_user_login(form_data.username)
    if not user:
        hasher.verify(form_data.password, DUMMY_PH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    if not hasher.verify(form_data.password, user.hashed_passw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )


    token = create_access_token(
        data={"sub": user.user_id.hex},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserPublicInfo)
async def read_me(current = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = AuthRepository(db)
    user = repo.search_user_by_id(UUID(current.get("user_id")))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not Validate Credentials")
    return user
