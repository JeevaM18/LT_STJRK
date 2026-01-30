from fastapi import APIRouter, UploadFile, File
from routes.process import process_sld

router = APIRouter(prefix="/api")

@router.post("/upload-sld")
async def upload_sld(file: UploadFile = File(...)):
    return process_sld(file)
