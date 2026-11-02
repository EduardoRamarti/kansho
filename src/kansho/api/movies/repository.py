from math import ceil
from uuid import UUID, uuid4

from sqlalchemy import delete, func, null, select, update
from sqlalchemy.orm import Session

from kansho.models.director import DirectorORM
from kansho.models.genre import GenreORM
from kansho.models.movie import MovieORM


class MovieRespository:
    def __init__(self, db: Session):
        self.db = db

    def get_movie(self, movie_id:UUID) -> MovieORM | None:
        find_movie = select(MovieORM).where(MovieORM.id == movie_id)
        return self.db.execute(find_movie).scalar_one_or_none()

    def get_movie_by_title(self, title: str, movie_id: UUID | None = None) -> MovieORM | None:
        if movie_id:
            return self.db.scalar(select(MovieORM).where(MovieORM.title.ilike(title.strip()), MovieORM.id != movie_id))
        return self.db.scalar(select(MovieORM).where(MovieORM.title.ilike(title.strip())))

    def search(self, movie_name: str | None, order_by: str, direction: str, page: int, limit: int ) -> tuple[int, list[MovieORM]]:
        
        results = select(MovieORM)
        
        if movie_name:
            movie_name = movie_name.strip()
            # Concatena dinámicamente la cláusula WHERE a la consulta base. Sobreescribimos 'results' porque .where() devuelve una consulta nueva.
            results = results.where(MovieORM.title.ilike(f"%{movie_name}%"))
    
    
        total = self.db.scalar(select(func.count()).select_from(results.subquery())) or 0
        # 4. Viaja a la BD, ejecuta la consulta y rompe la tupla resultante para darnos el número entero puro (ej. 15).
        # 3. Prepara la instrucción "SELECT COUNT(*)".
        # 2. Prepara la instrucción "FROM" indicando de dónde va a contar.
        # 1. Toma nuestra consulta base (con todos sus filtros WHERE), la encierra en paréntesis y la vuelve una "tabla temporal".
        # 5. Defensa de Python: Si el conteo por alguna razón falla y devuelve 'None', asigna '0' por defecto.

        total_pages = ceil(total/limit)

        if page > total_pages or total_pages == 0:
            return (total, [])


        if order_by == "title":
            order_col = func.lower(MovieORM.title) # if order_by == "title" else func.lower(MovieORM.director)
            # Tomamos el objeto de la columna (order_col), le indicamos la dirección (.asc o .desc) y finalmente concatenamos este "ORDER BY" a nuestra consulta principal 'results'.
            results = results.order_by(order_col.asc() if direction == "asc" else order_col.desc())
        else:
            order_col = func.lower(DirectorORM.name)
            results = results.join(MovieORM.director).order_by(order_col.asc() if direction == "asc" else order_col.desc())
            #.order_by(MovieORM.asc() if direction == "asc" else order_col.desc())
    

        skip = (page-1)*limit
        #db.execute(): Viaja a la BD y trae los registros (en formato de tuplas).
        # .scalars(): Rompe las tuplas y extrae el objeto MovieORM puro.
        # .all(): Recolecta todos los objetos puros y los mete en una lista de Python [MovieORM, MovieORM].
        items = self.db.execute(results.limit(limit).offset(skip)).scalars().all()

        return (total, items)

    def by_tags(self, genre_list: list[str]) -> list[MovieORM]:
        results = self.db.scalars(select(MovieORM).distinct().join(MovieORM.genres).where(GenreORM.name.in_(genre_list))).all()
        return results

    def ensure_director(self, name: str) -> DirectorORM:
        director = self.db.scalar(select(DirectorORM).where(DirectorORM.name.ilike(name.strip())))
        if not director:
            director = DirectorORM(
                id=uuid4(),
                name=name.strip()
            )
        return director

    def ensure_genre(self, genres:list[dict]) -> list[GenreORM]:
        genres_set= set()
        genres_list=[]
        for i in genres:
            genre_name = i['name'].strip().title()
            if genre_name in genres_set:
                continue
            genre = self.db.scalar(select(GenreORM).where(GenreORM.name.ilike(genre_name))) 
            genres_set.add(genre_name)
            if not genre:
                genre = GenreORM(
                    id=uuid4(),
                    name=genre_name
                )
            genres_list.append(genre)
        return genres_list

    def create_movie(self, title: str, year: int, rating: float, description: str, director: dict, genres: list[dict]) -> MovieORM:
        director_record = self.ensure_director(director.get("name"))
        genres_record = self.ensure_genre(genres)
        movie = MovieORM(
            id=uuid4(),
            title=title.strip(), 
            year=year,
            rating=rating,
            description=description,
            director=director_record,
            genres=genres_record
        )
        self.db.add(movie)
        self.db.commit()
        self.db.refresh(movie)
        return movie

    def full_movie_update(self, movie_id: UUID, title: str, year: int, rating: float, description: str, director: dict, genres: list[dict]):
        movie = self.get_movie(movie_id=movie_id)
        director = self.ensure_director(director.get('name'))
        genres = self.ensure_genre(genres)
        movie.director = director
        movie.genres = genres
        movie.title = title
        movie.year = year
        movie.rating = rating
        movie.description = description
        self.db.commit()
        return movie

    def partial_movie_update(self, movie_id: UUID, title: str|None, year: int|None, rating: float|None, description: str|None, director: dict|None, genres: list[dict]|None):
        movie = self.db.get(MovieORM, movie_id)
        if director is not None:
            director_record = self.ensure_director(director['name'])
            movie.director = director_record
        if genres is not None:
            genres_list = self.ensure_genre(genres)
            movie.genres = genres_list
        if title:
            movie.title = title.strip()
        if year:
            movie.year = year
        if rating:
            movie.rating = rating
        if description is not None:
            movie.description = description
        self.db.commit()
        self.db.refresh(movie)
        return movie

    def delete_movie(self, movie_id: UUID):
        delete_movie = delete(MovieORM).where(MovieORM.id == movie_id)
        result = self.db.execute(delete_movie)
        self.db.commit()
        return result.rowcount > 0