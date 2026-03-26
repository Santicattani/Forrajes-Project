import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from _app.database import engine, Base

load_dotenv()

db_error = None
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    db_error = str(e)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health():
    db_url = os.getenv("DATABASE_URL", "NOT_SET")
    return {"status": "ok" if not db_error else "error", "step": "con_create_all", "db": db_url[:30], "error": db_error}
