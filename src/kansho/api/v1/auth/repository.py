

from uuid import UUID, uuid4

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from kansho.models.user import UserORM


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_user_by_id(self, user_id: UUID):
        return self.db.get(UserORM, user_id)

    def search_user(self, username: str , email: str):
        query = select(exists().where(or_(UserORM.username.ilike(username), UserORM.email.ilike(email))))
        return self.db.scalar(query)


    def create_new_user(self, username: str, email: str, passw: str) -> UserORM:
        new_user = UserORM(
            user_id = uuid4(),
            username = username,
            email = email,
            hashed_passw = passw
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user