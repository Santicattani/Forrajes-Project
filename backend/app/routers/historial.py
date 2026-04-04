from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from jose import jwt
import os

from app.database import get_db
from app.models.user import User
from app.models.campo import Campo
from app.services.meteostat import obtener_historial

router = APIRouter(prefix="/historial", tags=["historial"])

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


@router.get("/{campo_id}")
async def historial_campo(
    campo_id: int,
    token: str,
    fecha_inicio: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    if fecha_fin < fecha_inicio:
        raise HTTPException(status_code=400, detail="fecha_fin debe ser posterior a fecha_inicio")
    if (fecha_fin - fecha_inicio).days > 365:
        raise HTTPException(status_code=400, detail="El rango máximo es 365 días")
    if fecha_fin >= date.today():
        raise HTTPException(status_code=400, detail="Solo se permiten fechas pasadas")

    user = get_user(token, db)
    campo = db.query(Campo).filter(Campo.id == campo_id, Campo.user_id == user.id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")

    dias = await obtener_historial(campo.latitud, campo.longitud, fecha_inicio, fecha_fin)
    return {
        "campo": campo.nombre,
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        "dias": dias,
    }
