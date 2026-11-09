from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.kansho.core.db import Base

if TYPE_CHECKING:
    from .director import DirectorORM
    from .genre import GenreORM

movie_genres = Table( # Es una Table, NO una clase ORM
    "movie_genres", #nombre de la tabla
    Base.metadata, # la registra junto a tus otras tablas para que se cree al hacer create_all
    # Se crean las columnas movie_id, genre_id
    # Ambas son primary_key, de esta manera solo se registra una combinacion por relacion: m1 - g1, m1-g2, etc...
    # ondelete="CASCADE": es una regla en la base de datos. Si borras una película (o un género), sus filas en movie_genres se borran automáticamente. Solo se borra el vínculo, no el género ni la película del otro lado.
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)


class MovieORM(Base):
    __tablename__ = "movies" #set table name
    __table_args__ = (UniqueConstraint("title", name="unique_movie_title"),)

    # Attributes for colums
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    image_url = mapped_column(String(300), nullable=True)

    director_id: Mapped[UUID] = mapped_column(ForeignKey("directors.id")) # Crea la columna de director como FK
    # Relación muchos a uno: cada película tiene un director.
    # No crea columna; usa director_id para cargar el objeto DirectorORM completo
    # (peli.director.name en vez de buscar el director a mano con el id).
    # back_populates="movies" apunta al atributo DirectorORM.movies:
    # ambos lados se sincronizan en memoria (al asignar peli.director, nolan.movies se actualiza solo)
    director: Mapped[DirectorORM] = relationship(back_populates="movies")

    # list[...], porque es muchos a muchos.
    # secondary=movie_genres: le dice a SQLAlchemy “para llegar del otro lado, pasa por esta tabla intermedia”
    # back_populates: sincroniza los dos lados en memoria (peli.genres ↔ scifi.movies).
    # lazy="selectin": controla cuándo se cargan los datos. Al consultar películas, SQLAlchemy trae de inmediato sus géneros en una segunda consulta con WHERE movie_id IN (...)
    # passive_deletes=True: le dice a SQLAlchemy “no borres tú las filas de movie_genres cuando elimine una película; deja que la base de datos lo haga con el CASCADE”
    genres: Mapped[list[GenreORM]]= relationship(secondary = movie_genres, back_populates="movies", lazy="selectin",passive_deletes=True)
