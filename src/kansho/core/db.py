import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

#Para conectarse a la BD, si no hay un env crea un sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./movies.db")
#print("Connected to: ", DATABASE_URL)

engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False} # si es sqlite apagar hilos para asincronismo 

engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs) # echo imprime el codigo SQL puro. future, version 2 de sqlalchemy 

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session) 
# sessionmaker configura la fábrica de sesiones:
# - bind=engine: Conecta las sesiones a tu motor de base de datos físico.
# - autocommit=False: Exige usar db.commit() manualmente, protegiendo transacciones complejas para no guardar datos a medias.
# - autoflush=False: Evita que SQLAlchemy sincronice datos a la BD de forma automática y prematura antes del commit.
# - class_=Session: Instancia la clase estándar de SQLAlchemy para darnos acceso a los métodos .query(), .add(), etc.


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal() # 1. Crea una sesión exclusiva para la petición HTTP entrante.
    try:
        yield db # 2. Pausa la función y le "presta" la sesión al endpoint para que haga sus consultas.
    finally:
        db.close() # 3. Al terminar (con éxito o error), obliga a cerrar la conexión para evitar saturar la BD.

