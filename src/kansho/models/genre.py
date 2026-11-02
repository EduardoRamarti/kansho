from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Uuid
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.kansho.core.db import Base

if TYPE_CHECKING:
    from .movie import MovieORM

class GenreORM(Base):
    __tablename__ = "genres"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    # Mapped[list["MovieORM"]]: scifi.movies devuelve la lista de películas de ese género. "MovieORM" va entre comillas porque esa clase se define más abajo.
    # secondary=movie_genres: le dice a SQLAlchemy “para llegar del otro lado, pasa por esta tabla intermedia”
    # back_populates="genres": apunta a MovieORM.genres.
    # lazy="selectin" carga las películas de inmediato en una consulta extra (WHERE ... IN).
    movies: Mapped[list["MovieORM"]] = relationship(
        secondary="movie_genres",
        back_populates="genres",
        lazy="selectin"
    )
