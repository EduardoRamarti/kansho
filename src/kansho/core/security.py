
import os
from datetime import datetime, timedelta, timezone

# OAuth2PasswordBearer → herramienta ya hecha para leer tokens del tipo “Bearer” de las peticiones.
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") # Creas un objeto de esa clase, configurado con la ruta de tu login


# Cuando el usuario demuestra quién es (usuario y contraseña correctos), esta función le fabrica su token con fecha de expiración
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy() # copia el diccionario 
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) # tiempo de expiracion del token 
    to_encode.update({"exp":expire}) # agrega el tiempo de expiracion al diccionario
    token = encode(payload= to_encode, key=SECRET_KEY, algorithm=ALGORITHM) 
    # crea el jwt: usa el payload como contenido, con la key genera la firma y con el algorithm el metodo de la firma 
    return token

# abre un token y verifica que la firma sea válida y que no haya expirado, comprueba que el token sea autentico
def decode_token(token: str) -> dict:
    playload = decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return playload

# dependencia que pones en los endpoints protegidos
def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException( # Creando la excepción 
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authenticated",
        headers={"WWW_Authenticate": "Bearer"}
    )

    try:
        playload = decode_token(token)
        subject: str | None = playload.get("sub")
        username: str | None = playload.get("username")
        if not subject or not username:
            raise credentials_exception
        return {"email": subject, "username": username}
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired Token",
            headers={"WWW_Authenticate": "Bearer"}
        )
    except InvalidTokenError:
        raise credentials_exception