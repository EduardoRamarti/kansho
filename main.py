from datetime import datetime
from typing import Union
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

MOVIES = [
    {
        "id": "ce473c72a82b4121b0b28c0f9f79e680",
        "title": "Interstellar",
        "year": 2014,
        "genres": ["Science Fiction", "Drama", "Adventure"],
        "director": "Christopher Nolan",
        "rating": 8.7,
        "description": "A team of astronauts travels through a wormhole in search of a habitable planet to save humanity from an environmental crisis on Earth, while one father struggles with the cost of leaving his family behind.",
    },
    {
        "id": "ec51efd4a5e24c3ab11ec95e93fe9253",
        "title": "Titanic",
        "year": 1997,
        "genres": ["Romance", "Drama", "History"],
        "director": "James Cameron",
        "rating": 7.9,
        "description": "A young aristocratic woman and a free-spirited artist from different social classes fall in love aboard the RMS Titanic, facing personal conflicts and tragedy when the ship strikes an iceberg.",
    },
    {
        "id": "139a9ea658484738b227f7dec6acd36e",
        "title": "The Godfather",
        "year": 1972,
        "genres": ["Crime", "Drama", "Thriller"],
        "director": "Francis Ford Coppola",
        "rating": 9.2,
        "description": "The aging patriarch of a powerful Italian-American crime family passes control of his empire to his reluctant youngest son, Michael Corleone, whose pursuit of power transforms him into a ruthless mafia leader.",
    },
    {
        "id": "43621b55c4ef46ee9f34e6df3bffcdc5",
        "title": "Jurassic Park",
        "year": 1993,
        "genres": ["Adventure", "Science Fiction", "Thriller"],
        "director": "Steven Spielberg",
        "rating": 8.2,
        "description": "A billionaire creates a theme park populated by genetically engineered dinosaurs, but a security failure causes the prehistoric creatures to escape, leaving a group of visitors fighting to survive.",
    },
    {
        "id": "ba73f214efcf4ff2a882be40e5985302",
        "title": "Coco",
        "year": 2017,
        "genres": ["Animation", "Adventure", "Comedy", "Family"],
        "director": "Lee Unkrich",
        "rating": 8.4,
        "description": "Miguel, a young boy who dreams of becoming a musician despite his family's ban on music, accidentally enters the Land of the Dead, where he uncovers family secrets and discovers the importance of remembering loved ones.",
    },
    {
        "id": "55b5e0a0960a496a82417f6271bb7215",
        "title": "The Matrix",
        "year": 1999,
        "genres": ["Science Fiction", "Action", "Thriller"],
        "director": "Lana and Lilly Wachowski",
        "rating": 8.7,
        "description": "A computer hacker named Neo discovers that the world he knows is a simulated reality created by intelligent machines. Joining a rebellion, he fights to free humanity and uncover his extraordinary potential.",
    },
    {
        "id": "28e2fd3e93f040488aa4849f46ec5145",
        "title": "Toy Story",
        "year": 1995,
        "genres": ["Animation", "Adventure", "Comedy", "Family"],
        "director": "John Lasseter",
        "rating": 8.3,
        "description": "When a new action figure named Buzz Lightyear becomes the favorite toy of their owner, Andy, Woody the cowboy doll grows jealous. The two rivals become lost together and must work as a team to return home.",
    },
    {
        "id": "bfc32b9c78f241b78792408a3081b6fa",
        "title": "Gladiator",
        "year": 2000,
        "genres": ["Action", "Drama", "Adventure", "History"],
        "director": "Ridley Scott",
        "rating": 8.5,
        "description": "After a corrupt Roman emperor murders his family and condemns him to slavery, a once-renowned general named Maximus becomes a gladiator and seeks justice and revenge in the arena.",
    },
    {
        "id": "59e0b72fc09b46c685cde928583a113d",
        "title": "Avatar",
        "year": 2009,
        "genres": ["Science Fiction", "Action", "Adventure", "Fantasy"],
        "director": "James Cameron",
        "rating": 7.9,
        "description": "A paraplegic former Marine travels to Pandora, an alien moon rich in natural resources, where he inhabits a genetically engineered body and becomes torn between the human mission and protecting the indigenous Na'vi people.",
    },
    {
        "id": "031fc790fc564712846ade624e6b5751",
        "title": "Back to the Future",
        "year": 1985,
        "genres": ["Science Fiction", "Adventure", "Comedy"],
        "director": "Robert Zemeckis",
        "rating": 8.5,
        "description": "Teenager Marty McFly accidentally travels back to 1955 in a time machine built by eccentric scientist Doc Brown. He must ensure his future parents fall in love while finding a way to return to his own time.",
    },
]

app = FastAPI(title="kansho")


class MovieBase(BaseModel):
    title: str
    year: int
    genres: list[str]
    director: str
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
    year: int | None = datetime.now().year
    genres: list[str] = Field(
        ...,
        description="Movie's genres",
        examples=[["Drama", "Humor", "Thriller"]]
    )
    director: str = Field(
        ...,
        min_length=10,
        max_length=50,
        description="Movie's director",
        examples=["Lana and Lilly Wachowski"]
    )
    rating: float | None = 0.0
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
    genres: list[str] = Field(
        ...,
        description="Movie's genres",
        examples=[["Drama", "Humor", "Thriller"]]
    )
    director: str = Field(
        ...,
        min_length=10,
        max_length=50,
        description="Movie's director",
        examples=["Lana and Lilly Wachowski"]
    )
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
    genres: list[str] | None = None
    director: str | None = None
    rating: float | None = None
    description: str | None = None


# Response Models 
class MoviePublic(MovieBase):
    id: str

class MovieSumary(BaseModel):
    id: str
    title: str
    director: str
    year: int

class MovieCreateResponse(MoviePublic):
    message: str

class MovieUpdateResponse(MoviePatch):
    message: str

@app.get("/")
def root():
    return {"message": "Hello world"}


@app.get("/movies", response_model=list[MoviePublic])
def list_movies(
    movie_name: str | None = Query(
        default=None, description="Search a movie by tittle"
    ),
):
    if movie_name:
        return [ movie for movie in MOVIES if movie_name.lower().strip() in movie["title"].lower()]
    else:
        return MOVIES


# response_model usa Union para permitir retornar dos esquemas distintos: detallado (MoviePublic) o resumido (MovieSumary).
@app.get("/movies/{movie_id}", response_model=Union[MoviePublic, MovieSumary], response_description="Movie Found")
def get_movie(
    movie_id: str,
    detailed: bool = Query(
        default=True, description="Include detailes about the movie"
    ),
):
    for movie in MOVIES:
        if movie['id'] == movie_id:
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
    new_movie = {
        "id": new_id,
        "title": movie_json.title,
        "year": movie_json.year,
        "genres": movie_json.genres,
        "director": movie_json.director,
        "rating" : movie_json.rating,
        "description" : movie_json.description,
    }
    MOVIES.append(new_movie)
    new_movie['message']="Movie Created"
    return  new_movie



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
            # if "title" in payload: movie["title"] = payload["title"]
            # if "year" in payload: movie["year"] = payload["year"]
            # if "genres" in payload: movie["genres"] = payload["genres"]
            # if "director" in payload: movie["director"] = payload["director"]
            # if "rating" in payload: movie["rating"] = payload["rating"]
            # if "description" in payload: movie["description"] = payload["description"]
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