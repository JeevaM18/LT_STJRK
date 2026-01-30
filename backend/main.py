from fastapi import FastAPI
from routes.upload import router as upload_router

app = FastAPI(title="Smart Electrical SLD AI Backend")

app.include_router(upload_router)

@app.get("/")
def health():
    return {"status": "SLD AI backend running"}
