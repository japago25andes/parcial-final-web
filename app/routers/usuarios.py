from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prestamo, Usuario
from app.schemas import Mensaje, UsuarioActualizar, UsuarioCrear, UsuarioSalida
from app.seguridad import encriptar_password, solo_admin

router = APIRouter(prefix="/usuarios", tags=["Usuarios"], dependencies=[Depends(solo_admin)])


def buscar_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    return usuario


def validar_correo_unico(db: Session, correo: str, excluir_id: int | None = None):
    consulta = db.query(Usuario).filter(Usuario.correo == correo)
    if excluir_id:
        consulta = consulta.filter(Usuario.id != excluir_id)
    if consulta.first():
        raise HTTPException(400, "Ya existe un usuario con ese correo")


@router.get("", response_model=list[UsuarioSalida], summary="Listar usuarios (admin)")
def listar(buscar: str | None = None, rol: str | None = None, db: Session = Depends(get_db)):
    """Filtros opcionales: `buscar` (nombre o correo) y `rol` (admin o lector)."""
    consulta = db.query(Usuario)
    if buscar:
        consulta = consulta.filter(Usuario.nombre.ilike(f"%{buscar}%") | Usuario.correo.ilike(f"%{buscar}%"))
    if rol:
        consulta = consulta.filter(Usuario.rol == rol)
    return consulta.order_by(Usuario.id).all()


@router.get("/{usuario_id}", response_model=UsuarioSalida, summary="Ver un usuario (admin)")
def obtener(usuario_id: int, db: Session = Depends(get_db)):
    return buscar_usuario(db, usuario_id)


@router.post("", response_model=UsuarioSalida, status_code=201, summary="Crear usuario (admin)")
def crear(datos: UsuarioCrear, db: Session = Depends(get_db)):
    correo = datos.correo.strip().lower()
    validar_correo_unico(db, correo)
    usuario = Usuario(
        nombre=datos.nombre,
        correo=correo,
        password_hash=encriptar_password(datos.password),
        rol=datos.rol,
        activo=datos.activo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioSalida, summary="Actualizar usuario (admin)")
def actualizar(usuario_id: int, datos: UsuarioActualizar, db: Session = Depends(get_db)):
    usuario = buscar_usuario(db, usuario_id)
    cambios = datos.model_dump(exclude_unset=True)
    if cambios.get("correo"):
        cambios["correo"] = cambios["correo"].strip().lower()
        validar_correo_unico(db, cambios["correo"], excluir_id=usuario_id)
    if cambios.get("password"):
        usuario.password_hash = encriptar_password(cambios.pop("password"))
    for campo, valor in cambios.items():
        if valor is not None:
            setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", response_model=Mensaje, summary="Eliminar usuario (admin)")
def eliminar(usuario_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(solo_admin)):
    usuario = buscar_usuario(db, usuario_id)
    if usuario.id == admin.id:
        raise HTTPException(400, "No puedes eliminar tu propio usuario")
    sin_devolver = (
        db.query(Prestamo)
        .filter(Prestamo.usuario_id == usuario_id, Prestamo.estado.in_(["activo", "vencido"]))
        .count()
    )
    if sin_devolver:
        raise HTTPException(400, "No se puede eliminar: el usuario tiene préstamos sin devolver")
    db.delete(usuario)  # también borra su historial de préstamos
    db.commit()
    return {"mensaje": "Usuario eliminado"}
