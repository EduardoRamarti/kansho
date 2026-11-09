
from math import ceil
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from psycopg import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from kansho.core.db import get_db
from kansho.core.security import get_current_user, oauth2_scheme
from kansho.services.file_storage import save_upload_file

from .repository import MovieRespository
from .schemas import (
    #MovieBase,
    MovieCreate,
    MovieCreateResponse,
    MoviePatch,
    MoviePublic,
    MovieSumary,
    MovieUpdate,
    MovieUpdateResponse,
    PaginatedMovies,
)

router = APIRouter(prefix="/movies", tags=["movies"])

# def get_fake_user():
#     return {"username": "Mike", "role": "admin"}

# @router.get("/me")
# def read_me(user: dict = Depends(get_fake_user)):
#     return {"user": user}

# Testing Async 

# @router.get("/sync")
# def sync_endpoint():
#     print("SYNC theread: ", threading.current_thread().name)
#     time.sleep(8)
#     return {"message": "Funcion sincrona termino"}

# @router.get("/async")
# async def async_endpoint():
#     print("ASYNC theread: ", threading.current_thread().name)
#     await asyncio.sleep(8)
#     return {"message": "Funcion asincrona termino"}

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
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
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

@router.get("/by-genre", response_model=list[MoviePublic])
def filter_by_genres(
    genres: list[str] = Query(
        ...,
        min_length=1,
        max_length=5,
        description="One or more genres. Example ?genres=drama&genres=humor"
    ),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    repo = MovieRespository(db)
    genre_list = [genre.strip().title() for genre in genres]

    return repo.by_tags(genre_list)

@router.get("/{movie_id}", response_model=MoviePublic | MovieSumary, response_description="Movie Found")
def get_movie(
    movie_id: UUID,
    detailed: bool = Query(
        default=True, description="Include detailes about the movie"
    ),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    repo = MovieRespository(db)
    movie = repo.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # model_validate() → Traduce y valida manualmente un objeto crudo de SQLAlchemy a este esquema de Pydantic.
    # (Nota: FastAPI hace esto en automático al salir si el endpoint tiene 'response_model').
    return MoviePublic.model_validate(movie, from_attributes=True) if detailed else MovieSumary.model_validate(movie, from_attributes=True)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=MovieCreateResponse, response_description="Movie created (ok)")
def create_movie(movie_json: Annotated[MovieCreate, Depends(MovieCreate.as_form)], image: UploadFile | None = File(None), db: Session = Depends(get_db), user=Depends(get_current_user)):

    repo = MovieRespository(db)

    if repo.get_movie_by_title(movie_json.title):
        raise HTTPException(status_code=409, detail="Movie already exists")
    saved = None
    try:
        if image is not None:
            saved = save_upload_file(image)
        image_url = saved["url"] if saved else None
        new_movie = repo.create_movie(
            title=movie_json.title,
            year=movie_json.year,
            rating=movie_json.rating,
            description=movie_json.description,
            director=movie_json.director.model_dump(),
            genres=[movie_genre.model_dump() for movie_genre in movie_json.genres],
            image_url=image_url
        )
        return new_movie
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This title already exist")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating movie")

@router.put("/{movie_id}", response_model=MovieUpdateResponse, response_description="Movie Updated")
def update_movie(movie_id: UUID, data: MovieUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = MovieRespository(db)
    if not repo.get_movie(movie_id=movie_id):
        raise HTTPException(status_code=404, detail="Movie not found")
    if data.title and repo.get_movie_by_title(title=data.title, movie_id=movie_id):
        raise HTTPException(status_code=409, detail="Movie already exists")
    try:
        movie = repo.full_movie_update(
            movie_id=movie_id,
            title=data.title,
            year=data.year,
            rating=data.rating,
            description=data.description,
            director=data.director.model_dump(),
            genres=[movie_genre.model_dump() for movie_genre in data.genres]
        )
        return movie
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict with existing data")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"ERROR DE SQLALCHEMY: {e}")
        raise HTTPException(status_code=500, detail="Error updating movie")

@router.patch("/{movie_id}", response_model=MovieUpdateResponse, response_description="Movie Updated", response_model_exclude_none=True) #exclude_none quita los que tengan none de la respuesta
def update_movie_patch(movie_id: UUID, data: MoviePatch, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = MovieRespository(db)
    if not repo.get_movie(movie_id=movie_id):
        raise HTTPException(status_code=404, detail="Movie not found")
    if data.title and repo.get_movie_by_title(title=data.title, movie_id=movie_id):
        raise HTTPException(status_code=409, detail="Movie already exists")
    update_data = data.model_dump(exclude_unset=True)
    director_data = update_data.pop("director", None)
    genres = update_data.pop("genres", None)
    try:
        record = repo.partial_movie_update(
            movie_id=movie_id,
            title=data.title,
            year=data.year,
            rating=data.rating,
            description=data.description,
            director=director_data,
            genres=genres
        )
        return record
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This title already exist")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"ERROR DE SQLALCHEMY: {e}")
        raise HTTPException(status_code=500, detail="Error updating movie")

@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = MovieRespository(db)

    if not repo.get_movie(movie_id=movie_id):
        raise HTTPException(status_code=404, detail="Movie not found")
    try:
        repo.delete_movie(movie_id=movie_id)
        return
    except SQLAlchemyError as e:
        db.rollback()
        print(f"ERROR DE SQLALCHEMY: {e}")
        raise HTTPException(status_code=500, detail="Error deleting movie")

@router.get("/secure")
def secure_endpoint(token: str = Depends(oauth2_scheme)): # Depends le dice a FastAPI: “antes de ejecutar este endpoint, consígueme este valor llamando a esta función”
    return {"message":"Token Access", "Token_received":token}