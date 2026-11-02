from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Genre(BaseModel):
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=30, 
        description="Movie's genre", 
        examples=["Drama", "Humor", "Thriller"]
        )
    model_config = ConfigDict(from_attributes=True)

class Director(BaseModel):
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=30, 
        description="Movie's director name", 
        examples=["Steven Spielberg"]
    )
    model_config = ConfigDict(from_attributes=True)

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
        examples=["Jurassic Park"]
    )
    # default_factory ejecuta la función cada vez que se crea un nuevo objeto, garantizando que el valor sea dinámico (como la hora actual) y no se quede "congelado" al iniciar el servidor.
    # DEFAULT FACTORY (Dinámico): Se usa para valores que requieren ejecutar una función.
    # Como el año o un ID, que necesitan calcularse en el milisegundo exacto de la petición.
    # year: int = Field(default_factory=lambda: datetime.now().year)
    year: int | None = Field(default_factory=lambda: datetime.now().year, examples=[1973])
    genres: list[Genre] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Movie's genres",
        examples=[[{"name": "Adventure"}, {"name": "Science Fiction"}, {"name": "Thriller"}]]
    )
    director: Director 
    rating: float | None = 8.2
    description: str = Field(
        ...,
        min_length=50,
        max_length=400,
        description="Movie's description ( min 50 chars and max 300 chars)",
        examples=["A billionaire creates a theme park populated by genetically engineered dinosaurs, but a security failure causes the prehistoric creatures to escape, leaving a group of visitors fighting to survive."]
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

class MoviePatchTemp(BaseModel):
    title: str | None = None
    year: int | None = None
    rating: float | None = None
    description: str | None = None

# Response Models 
class MoviePublic(MovieBase):
    id: UUID

    # Le da permiso a Pydantic de leer datos desde objetos ORM de SQLAlchemy (obj.atributo) 
    # y no solo desde diccionarios. Sin esto, FastAPI no podría traducir la base de datos a JSON.
    model_config = ConfigDict(from_attributes=True) # Para que pydantic sepa que va a recibir datos de sqlalchemy

class MovieSumary(BaseModel):
    id: UUID
    title: str
    director: Director
    year: int

    # Le da permiso a Pydantic de leer datos desde objetos ORM de SQLAlchemy (obj.atributo) 
    # y no solo desde diccionarios. Sin esto, FastAPI no podría traducir la base de datos a JSON.
    model_config = ConfigDict(from_attributes=True)

class MovieSumaryTemp(BaseModel):
    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)

class MovieCreateResponse(BaseModel):
    id: UUID
    title: str
    year: int
    rating: float
    description: str

    # Le da permiso a Pydantic de leer datos desde objetos ORM de SQLAlchemy (obj.atributo) 
    # y no solo desde diccionarios. Sin esto, FastAPI no podría traducir la base de datos a JSON.
    model_config = ConfigDict(from_attributes=True)

class MovieUpdateResponse(MoviePatch):
    model_config = ConfigDict(from_attributes=True)

class PaginatedMovies(BaseModel):
    page: int #= Field(..., min_length=1, description="Page calculated from amount of results")
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: str
    direction: str
    search: str | None
    items: list[MoviePublic]
