from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    campo_nombre: str | None = None
    latitud: float | None = None
    longitud: float | None = None

    model_config = {"from_attributes": True}
