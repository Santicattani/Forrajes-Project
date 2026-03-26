from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
import os

from app.database import get_db
from app.models.user import User
from app.models.campo import Campo
from app.services.clima import obtener_pronostico

router = APIRouter(prefix="/clima", tags=["clima"])

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def get_user(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/pronostico/{campo_id}")
async def pronostico(campo_id: int, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    campo = db.query(Campo).filter(Campo.id == campo_id, Campo.user_id == user.id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    dias = await obtener_pronostico(campo.latitud, campo.longitud)
    return {"dias": dias}
