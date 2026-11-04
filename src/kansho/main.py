from dotenv import load_dotenv
from fastapi import FastAPI

from kansho.api.v1.auth.router import router as auth_router
from kansho.api.v1.movies.router import router as movie_router
from kansho.core.db import Base, engine

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="kansho")
    Base.metadata.create_all(bind=engine) #dev enviroment
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(movie_router) # Includes the  movie router 

    @app.get("/")
    def root():
        return {"message": "OK"}

    return app

app = create_app()