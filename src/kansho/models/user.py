

from uuid import UUID

from sqlalchemy import String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.kansho.core.db import Base


class UserORM(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", name="unique_username"),UniqueConstraint("email", name="unique_email"))
    user_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, index=True, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_passw: Mapped[str] = mapped_column(String, nullable=False)