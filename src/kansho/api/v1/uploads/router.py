
from fastapi import APIRouter, Depends, File, UploadFile

from kansho.core.security import get_current_user
from kansho.services.file_storage import save_upload_file

router = APIRouter(prefix="/upload", tags=["uploads"])

MEDIA_DIR = "media"

# @router.post("/bytes")
# async def upload_bytes(file: bytes = File(...)):
#     return {
#         "file_name": "archivo_subido",
#         "size_bytes": len(file)
#     }

# @router.post("/file")
# async def upload_file(file: UploadFile = File(...)):
#     return {
#         "file_name":file.filename,
#         "content_type":file.content_type
#     }

@router.post("/save")
async def save_file(file: UploadFile = File(...), user=Depends(get_current_user)):

    saved = save_upload_file(file)

    return {
        "filename": saved["filename"],
        "content_type": saved["content_type"],
        "url": saved["url"]
    }

