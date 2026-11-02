from dotenv import load_dotenv
from fastapi import FastAPI

from kansho.api.v1.movies.router import router as movie_router
from kansho.core.db import Base, engine

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="kansho")
    Base.metadata.create_all(bind=engine) #dev enviroment
    app.include_router(movie_router) # Includes the router 

    @app.get("/")
    def root():
        return {"message": "OK"}

    return app

app = create_app()