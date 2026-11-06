import os
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(prefix="/upload", tags=["uploads"])

MEDIA_DIR = "media"

@router.post("/bytes")
async def upload_bytes(file: bytes = File(...)):
    return {
        "file_name": "archivo_subido",
        "size_bytes": len(file)
    }

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    return {
        "file_name":file.filename,
        "content_type":file.content_type
    }

@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    if file.content_type not in ["image/png", "image/jpeg"]: #si el tipo de archivo es diferente al de la lista 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PNG or JPEG images are allowed")

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

