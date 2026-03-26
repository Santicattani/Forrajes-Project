from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt
import os

from app.database import get_db
from app.models.user import User
from app.models.campo import Campo

router = APIRouter(prefix="/campos", tags=["campos"])

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


class CampoRequest(BaseModel):
    nombre: str
    latitud: float
    longitud: float


class CampoResponse(BaseModel):
    id: int
    nombre: str
    latitud: float
    longitud: float
    model_config = {"from_attributes": True}


@router.get("", response_model=list[CampoResponse])
def listar_campos(token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    return user.campos


@router.post("", response_model=CampoResponse, status_code=201)
def crear_campo(body: CampoRequest, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    campo = Campo(user_id=user.id, nombre=body.nombre, latitud=body.latitud, longitud=body.longitud)
    db.add(campo)
    db.commit()
    db.refresh(campo)
    return campo


@router.delete("/{campo_id}", status_code=204)
def eliminar_campo(campo_id: int, token: str, db: Session = Depends(get_db)):
    user = get_user(token, db)
    campo = db.query(Campo).filter(Campo.id == campo_id, Campo.user_id == user.id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    db.delete(campo)
    db.commit()
