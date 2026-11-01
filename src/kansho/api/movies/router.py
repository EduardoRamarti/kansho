from math import ceil
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from kansho.core.db import get_db

from .repository import MovieRespository
from .schemas import (
    MovieBase,
    MovieCreate,
    MoviePatch,
    MoviePublic,
    MovieSumary,
    MovieUpdate,
    PaginatedMovies,
)

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=PaginatedMovies)
def list_movies(
    name: str | None = Query(
        default=None,
        deprecated=True,
        description="Deprecated param, use 'search' instead"
    ),
    movie_name: str | None = Query(
        default=None, 
        description="Search a movie by tittle",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"
    ),
    # Set a limit for how manny movies show per page
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Total results (1-50)"
    ),
    # Set where to start showing the movies, example: from which movie start 
    page: int = Query(
        default=1,
        ge=1,
        description="Set page to show items"
    ),
    # Literal["id", "title"] restringe este parámetro para que SOLO acepte exactamente esas dos palabras. 
    # Si el usuario intenta mandar "year" o cualquier otra cosa, FastAPI lo bloquea automáticamente con un error 422.
    order_by: Literal["title", "director"] = Query(
        "title", description="Order by Movie title or Movie Director"
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Order direction"
    ),
    db: Session = Depends(get_db)
):
    repo = MovieRespository(db)
    movie_name = movie_name or name

    total, items = repo.search(
        movie_name=movie_name,
        order_by=order_by,
        direction=direction,
        page=page,
        limit=limit
    )
    total_pages = ceil(total/limit)
    if total_pages == 0:
        has_prev = False
        has_next = False 
    else:
        has_prev = page > 1
        has_next = page < total_pages
        # PaginatedMovies(total=total, limit=limit, offset=offset, items=items)
    return PaginatedMovies(
        page=page,
        per_page=limit,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=movie_name,
        items=items
    )
