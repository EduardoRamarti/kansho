import os
import shutil
import uuid

from fastapi import File, HTTPException, UploadFile, status

MEDIA_DIR = "media"
ALLOW_MIME = ["image/png", "image/jpeg"]

def ensure_media_dir() -> None:
    os.makedirs(MEDIA_DIR, exist_ok=True)

def save_upload_file(file: UploadFile) -> dict:
    if file.content_type not in ALLOW_MIME: #si el tipo de archivo es diferente al de la lista 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PNG or JPEG images are allowed")

    ensure_media_dir()

    ext = os.path.splitext(file.filename)[1] # 1. saco ".png" del nombre original (solo texto)
    filename = f"{uuid.uuid4().hex}{ext}"  # 2. armo un nombre nuevo unico: "3f9a...e2.png" (solo texto)
    file_path = os.path.join(MEDIA_DIR, filename) # 3. armo la ruta destino: "kansho/media/3f9a...e2.png" (solo texto)

    with open(file_path, "wb") as buffer: # wb → crear el archivo y escribe en binario 
        shutil.copyfileobj(file.file, buffer) # copyfileobj → Copia de un objeto archivo abierto a otro (la de tu código)
    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}"
    }

