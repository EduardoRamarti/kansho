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

class DirectorORM(Base):
    __tablename__ = "directors"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Relación uno a muchos: un director tiene varias películas.
    # movies No crea columna en "directors"; la FK real está en movies.director_id. (tabla de movies)
    # back_populates="director" la sincroniza con MovieORM.director (ambos nombres deben coincidir).
    movies: Mapped[list[MovieORM]] = relationship(back_populates="director")


