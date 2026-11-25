from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import LoginEntrada, PerfilActualizar, RegistroEntrada, TokenSalida, UsuarioSalida
from app.seguridad import autenticar, crear_token, encriptar_password, usuario_actual

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenSalida, summary="Iniciar sesión (JSON)")
def login(datos: LoginEntrada, db: Session = Depends(get_db)):
    """Recibe correo y contraseña. Devuelve el token y los datos del usuario.

    El token se envía en las siguientes peticiones con el header
    `Authorization: Bearer <token>`.
    """
    usuario = autenticar(db, datos.correo, datos.password)
    return {"access_token": crear_token(usuario), "token_type": "bearer", "usuario": usuario}


@router.post("/token", include_in_schema=False)
def token_swagger(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Lo usa el botón Authorize de Swagger (username = correo)."""
    usuario = autenticar(db, form.username, form.password)
    return {"access_token": crear_token(usuario), "token_type": "bearer"}


@router.post("/registro", response_model=UsuarioSalida, status_code=201, summary="Registrar un lector nuevo")
def registro(datos: RegistroEntrada, db: Session = Depends(get_db)):
    """Crea una cuenta con rol **lector**. No requiere token."""
    correo = datos.correo.strip().lower()
    if db.query(Usuario).filter(Usuario.correo == correo).first():
        raise HTTPException(400, "Ya existe un usuario con ese correo")
    usuario = Usuario(
        nombre=datos.nombre, correo=correo, password_hash=encriptar_password(datos.password), rol="lector"
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/perfil", response_model=UsuarioSalida, summary="Ver mi perfil")
def ver_perfil(usuario: Usuario = Depends(usuario_actual)):
    return usuario


@router.put("/perfil", response_model=UsuarioSalida, summary="Actualizar mi nombre o contraseña")
def actualizar_perfil(
    datos: PerfilActualizar, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)
):
    if datos.nombre:
        usuario.nombre = datos.nombre
    if datos.password:
        usuario.password_hash = encriptar_password(datos.password)
    db.commit()
    db.refresh(usuario)
    return usuario
