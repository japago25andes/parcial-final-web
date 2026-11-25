"""Contraseñas, tokens JWT y control de acceso por rol."""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario

SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-parcial-programacion-web")
ALGORITHM = "HS256"
HORAS_VALIDEZ_TOKEN = 24

# tokenUrl es el endpoint que usa el botón "Authorize" de Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="Iniciar sesión")


def encriptar_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def crear_token(usuario: Usuario) -> str:
    datos = {
        "sub": str(usuario.id),
        "nombre": usuario.nombre,
        "rol": usuario.rol,
        "exp": datetime.now(timezone.utc) + timedelta(hours=HORAS_VALIDEZ_TOKEN),
    }
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)


def autenticar(db: Session, correo: str, password: str) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.correo == correo.strip().lower()).first()
    if not usuario or not verificar_password(password, usuario.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos")
    if not usuario.activo:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "El usuario está inactivo")
    return usuario


def usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """Dependencia: exige un token válido y devuelve el usuario que lo envía."""
    error = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Token inválido o expirado. Inicia sesión de nuevo.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario = db.get(Usuario, int(datos["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise error
    if not usuario or not usuario.activo:
        raise error
    return usuario


def solo_admin(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    """Dependencia: además del token, exige que el usuario sea admin."""
    if usuario.rol != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo un administrador puede hacer esta acción")
    return usuario
