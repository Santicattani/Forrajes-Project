import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from _app.database import engine, Base
from _app.models import user, campo  # noqa: registrar modelos
from _app.routers import auth, clima, campos

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma Forrajes", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(campos.router, prefix="/api/v1")
app.include_router(clima.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


# Servir frontend estático — debe ir al final
_public = os.path.join(os.getcwd(), "public")
if not os.path.isdir(_public):
    _public = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
if os.path.isdir(_public):
    app.mount("/", StaticFiles(directory=_public, html=True), name="static")
