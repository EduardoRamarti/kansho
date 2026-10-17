from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

MOVIES = [
    {
        "id": "ce473c72a82b4121b0b28c0f9f79e680",
        "title": "Interstellar",
        "year": 2014,
        "genres": [{"name": "Science Fiction"}, {"name": "Drama"}, {"name": "Adventure"}],
        "director": {"name": "Christopher Nolan"},
        "rating": 8.7,
        "description": "A team of astronauts travels through a wormhole in search of a habitable planet to save humanity from an environmental crisis on Earth, while one father struggles with the cost of leaving his family behind.",
    },
    {
        "id": "ec51efd4a5e24c3ab11ec95e93fe9253",
        "title": "Titanic",
        "year": 1997,
        "genres": [{"name": "Romance"}, {"name": "Drama"}, {"name": "History"}],
        "director": {"name": "James Cameron"},
        "rating": 7.9,
        "description": "A young aristocratic woman and a free-spirited artist from different social classes fall in love aboard the RMS Titanic, facing personal conflicts and tragedy when the ship strikes an iceberg.",
    },
    {
        "id": "139a9ea658484738b227f7dec6acd36e",
        "title": "The Godfather",
        "year": 1972,
        "genres": [{"name": "Crime"}, {"name": "Drama"}, {"name": "Thriller"}],
        "director": {"name": "Francis Ford Coppola"},
        "rating": 9.2,
        "description": "The aging patriarch of a powerful Italian-American crime family passes control of his empire to his reluctant youngest son, Michael Corleone, whose pursuit of power transforms him into a ruthless mafia leader.",
    },
    {
        "id": "43621b55c4ef46ee9f34e6df3bffcdc5",
        "title": "Jurassic Park",
        "year": 1993,
        "genres": [{"name": "Adventure"}, {"name": "Science Fiction"}, {"name": "Thriller"}],
        "director": {"name": "Steven Spielberg"},
        "rating": 8.2,
        "description": "A billionaire creates a theme park populated by genetically engineered dinosaurs, but a security failure causes the prehistoric creatures to escape, leaving a group of visitors fighting to survive.",
    },
    {
        "id": "ba73f214efcf4ff2a882be40e5985302",
        "title": "Coco",
        "year": 2017,
        "genres": [{"name": "Animation"}, {"name": "Adventure"}, {"name": "Comedy"}, {"name": "Family"}],
        "director": {"name": "Lee Unkrich"},
        "rating": 8.4,
        "description": "Miguel, a young boy who dreams of becoming a musician despite his family's ban on music, accidentally enters the Land of the Dead, where he uncovers family secrets and discovers the importance of remembering loved ones.",
    },
    {
        "id": "55b5e0a0960a496a82417f6271bb7215",
        "title": "The Matrix",
        "year": 1999,
        "genres": [{"name": "Science Fiction"}, {"name": "Action"}, {"name": "Thriller"}],
        "director": {"name": "Lana and Lilly Wachowski"},
        "rating": 8.7,
        "description": "A computer hacker named Neo discovers that the world he knows is a simulated reality created by intelligent machines. Joining a rebellion, he fights to free humanity and uncover his extraordinary potential.",
    },
    {
        "id": "28e2fd3e93f040488aa4849f46ec5145",
        "title": "Toy Story",
        "year": 1995,
        "genres": [{"name": "Animation"}, {"name": "Adventure"}, {"name": "Comedy"}, {"name": "Family"}],
        "director": {"name": "John Lasseter"},
        "rating": 8.3,
        "description": "When a new action figure named Buzz Lightyear becomes the favorite toy of their owner, Andy, Woody the cowboy doll grows jealous. The two rivals become lost together and must work as a team to return home.",
    },
    {
        "id": "bfc32b9c78f241b78792408a3081b6fa",
        "title": "Gladiator",
        "year": 2000,
        "genres": [{"name": "Action"}, {"name": "Drama"}, {"name": "Adventure"}, {"name": "History"}],
        "director": {"name": "Ridley Scott"},
        "rating": 8.5,
        "description": "After a corrupt Roman emperor murders his family and condemns him to slavery, a once-renowned general named Maximus becomes a gladiator and seeks justice and revenge in the arena.",
    },
    {
        "id": "59e0b72fc09b46c685cde928583a113d",
        "title": "Avatar",
        "year": 2009,
        "genres": [{"name": "Science Fiction"}, {"name": "Action"}, {"name": "Adventure"}, {"name": "Fantasy"}],
        "director": {"name": "James Cameron"},
        "rating": 7.9,
        "description": "A paraplegic former Marine travels to Pandora, an alien moon rich in natural resources, where he inhabits a genetically engineered body and becomes torn between the human mission and protecting the indigenous Na'vi people.",
    },
    {
        "id": "031fc790fc564712846ade624e6b5751",
        "title": "Back to the Future",
        "year": 1985,
        "genres": [{"name": "Science Fiction"}, {"name": "Adventure"}, {"name": "Comedy"}],
        "director": {"name": "Robert Zemeckis"},
        "rating": 8.5,
        "description": "Teenager Marty McFly accidentally travels back to 1955 in a time machine built by eccentric scientist Doc Brown. He must ensure his future parents fall in love while finding a way to return to his own time.",
    },
]

app = FastAPI(title="kansho")

class Genre(BaseModel):
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=30, 
        description="Movie's genre", 
        examples=["Drama", "Humor", "Thriller"]
        )

class Director(BaseModel):
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=30, 
        description="Movie's director name", 
        examples=["Christopher Nolan"]
    )

class MovieBase(BaseModel):
    title: str
    year: int
    genres: list[Genre]
    director: Director
    rating: float
    description: str

class MovieCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Movie's title ( min 3 chars and max 100 chars)",
        examples=["Matrix"]
    )
    # default_factory ejecuta la función cada vez que se crea un nuevo objeto, garantizando que el valor sea dinámico (como la hora actual) y no se quede "congelado" al iniciar el servidor.
    # DEFAULT FACTORY (Dinámico): Se usa para valores que requieren ejecutar una función.
    # Como el año o un ID, que necesitan calcularse en el milisegundo exacto de la petición.
    year: int | None = Field(default_factory=lambda: datetime.now().year)
    genres: list[Genre] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Movie's genres",
        examples=[[{"name":"Drama"}, {"name":"Humor"}, {"name":"Thriller"}]]
    )
    director: Director 
    rating: float | None = 10.0
    description: str = Field(
        ...,
        min_length=50,
        max_length=400,
        description="Movie's description ( min 50 chars and max 300 chars)",
        examples=["A computer hacker named Neo discovers that the world he knows is a simulated reality created by intelligent machines. Joining a rebellion, he fights to free humanity and uncover his extraordinary potential."]
    )
    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value:str) -> str:
        if "spam" in value.lower():
            raise ValueError("The title cannot set this word: 'spam'")
        return value

class MovieUpdate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Movie's title ( min 3 chars and max 100 chars)",
        examples=["Matrix"]
    )
    year: int
    genres: list[Genre] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Movie's genres",
        examples=[[{"name":"Drama"}, {"name":"Humor"}, {"name":"Thriller"}]]
    )
    director: Director
    rating: float
    description: str = Field(
        ...,
        min_length=50,
        max_length=400,
        description="Movie's description ( min 50 chars and max 300 chars)",
        examples=["A computer hacker named Neo discovers that the world he knows is a simulated reality created by intelligent machines. Joining a rebellion, he fights to free humanity and uncover his extraordinary potential."]
    )

class MoviePatch(BaseModel):
    title: str | None = None
    year: int | None = None
    genres: list[Genre] | None = None
    director: Director | None = None
    rating: float | None = None
    description: str | None = None


# Response Models 
class MoviePublic(MovieBase):
    id: UUID

class MovieSumary(BaseModel):
    id: UUID
    title: str
    director: Director
    year: int

class MovieCreateResponse(MoviePublic):
    message: str

class MovieUpdateResponse(MoviePatch):
    message: str


class PaginatedMovies(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[MoviePublic]


@app.get("/")
def root():
    return {"message": "Hello world"}


@app.get("/movies", response_model=PaginatedMovies)
def list_movies(
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
    offset: int = Query(
        default=0,
        ge=0,
        description="Avoid items before create the list"
    ),
    # Literal["id", "title"] restringe este parámetro para que SOLO acepte exactamente esas dos palabras. 
    # Si el usuario intenta mandar "year" o cualquier otra cosa, FastAPI lo bloquea automáticamente con un error 422.
    order_by: Literal["title", "director"] = Query(
        "title", description="Order by Movie title"
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Order direction"
    )
):

    results = MOVIES
    
    if movie_name:
        results = [ movie for movie in results if movie_name.lower().strip() in movie["title"].lower()]

    total = len(results)

    results = sorted(results, key=lambda movie: movie[order_by] if order_by == "title" else movie[order_by]["name"], reverse=(direction == "desc"))

    items = results[offset: offset+limit]

    return PaginatedMovies(total=total, limit=limit, offset=offset, items=items)


# response_model usa Union para permitir retornar dos esquemas distintos: detallado (MoviePublic) o resumido (MovieSumary).
# @app.get("/movies/{movie_id}", response_model=Union[MoviePublic, MovieSumary], response_description="Movie Found")
@app.get("/movies/{movie_id}", response_model=MoviePublic | MovieSumary, response_description="Movie Found")
def get_movie(
    movie_id: UUID,
    detailed: bool = Query(
        default=True, description="Include detailes about the movie"
    ),
):
    for movie in MOVIES:
        if movie['id'] == movie_id.hex:
            if detailed:
                return movie
            return {
                    "id": movie["id"],
                    "title": movie["title"],
                    "director": movie["director"],
                    "year": movie["year"]
                }
    raise HTTPException(status_code=404, detail="Movie Not Found")



@app.post("/create_movie", status_code=201, response_model=MovieCreateResponse)
def create_movie(movie_json: MovieCreate):
    new_id = uuid4().hex
    # new_movie = {
    #     "id": new_id,
    #     "title": movie_json.title,
    #     "year": movie_json.year,
    #     "genres": movie_json.genres,
    #     "director": movie_json.director,
    #     "rating" : movie_json.rating,
    #     "description" : movie_json.description,
    # }
    new_movie = movie_json.model_dump()
    new_movie["id"] = new_id
    MOVIES.append(new_movie)
    return  {**new_movie, "message":"Movie created"}



@app.put("/movies/{movie_id}", response_model=MovieUpdateResponse, response_description="Movie Updated")
def update_movie(movie_id: str, data: MovieUpdate):
    for movie in MOVIES:
        if movie["id"] == movie_id:
            movie["title"] = data.title
            movie["year"] = data.year
            movie["genres"] = data.genres
            movie["director"] = data.director
            movie["rating"] = data.rating
            movie["description"] = data.description
            # El operador ** (unpacking) "abre" el diccionario de la película.
            # **movie "desempaqueta" el diccionario original, extrayendo todas sus llaves y valores al nivel principal para crear un diccionario plano.
            return { **movie, "message":"Movie Updated"} 
    raise HTTPException(status_code=404, detail="Movie not found")



@app.patch("/movies/{movie_id}", response_model=MovieUpdateResponse, response_description="Movie Updated", response_model_exclude_none=True) #exclude_none quita los que tengan none de la respuesta
def update_movie_patch(movie_id: str, data: MoviePatch):
    for movie in MOVIES:
        if movie["id"] == movie_id:
            payload = data.model_dump(exclude_unset=True) # model_dump() → convierte tu modelo de datos en un diccionario de Python, pero ignorando cualquier campo que el usuario no haya enviado explícitamente.
            movie.update(payload)
            return {"message":"Movie Updated", **movie}
    raise HTTPException(status_code=404, detail="Movie not found")



@app.delete("/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: str):
    for index, movie in enumerate(MOVIES):
        if movie["id"] == movie_id:
            MOVIES.pop(index)
            return 
    raise HTTPException(status_code=404, detail="Movie not found")