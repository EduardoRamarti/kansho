import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from kansho.api.v1.auth.router import router as auth_router
from kansho.api.v1.movies.router import router as movie_router
from kansho.api.v1.uploads.router import router as upload_router
from src.kansho.core.db import Base, engine

load_dotenv()

MEDIA_DIR = "media"

def create_app() -> FastAPI:
    app = FastAPI(title="kansho")
    print("Tablas registradas:", list(Base.metadata.tables.keys()))
    print("Base de datos:", engine.url)
    Base.metadata.create_all(bind=engine)
    # Base.metadata.create_all(bind=engine) #dev enviroment
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(movie_router) # Includes the  movie router 
    app.include_router(upload_router)

    @app.get("/")
    def root():
        return {"message": "OK"}

    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    return app

app = create_app()