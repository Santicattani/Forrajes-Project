from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine, Base
from app.models import user, campo  # noqa: registrar modelos
from app.routers import auth, clima, campos, mercado, alfalfa, historial

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
app.include_router(mercado.router, prefix="/api/v1")
app.include_router(alfalfa.router, prefix="/api/v1")
app.include_router(historial.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
