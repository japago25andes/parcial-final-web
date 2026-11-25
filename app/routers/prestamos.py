from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Libro, Prestamo, Usuario
from app.schemas import Mensaje, PrestamoActualizar, PrestamoCrear, PrestamoSalida
from app.seguridad import solo_admin, usuario_actual

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])

MAX_PRESTAMOS_POR_USUARIO = 3
SIN_DEVOLVER = ["activo", "vencido"]


def actualizar_vencidos(db: Session):
    """Marca como 'vencido' todo préstamo activo cuya fecha límite ya pasó."""
    db.query(Prestamo).filter(Prestamo.estado == "activo", Prestamo.fecha_limite < date.today()).update(
        {"estado": "vencido"}
    )
    db.commit()


def buscar_prestamo(db: Session, prestamo_id: int, usuario: Usuario) -> Prestamo:
    prestamo = db.get(Prestamo, prestamo_id)
    if not prestamo:
        raise HTTPException(404, "Préstamo no encontrado")
    if usuario.rol != "admin" and prestamo.usuario_id != usuario.id:
        raise HTTPException(403, "Este préstamo no es tuyo")
    return prestamo


@router.get("", response_model=list[PrestamoSalida], summary="Listar todos los préstamos (admin)")
def listar(
    estado: str | None = None,
    usuario_id: int | None = None,
    db: Session = Depends(get_db),
    _=Depends(solo_admin),
):
    """Filtros opcionales: `estado` (activo, vencido, devuelto) y `usuario_id`."""
    actualizar_vencidos(db)
    consulta = db.query(Prestamo)
    if estado:
        consulta = consulta.filter(Prestamo.estado == estado)
    if usuario_id:
        consulta = consulta.filter(Prestamo.usuario_id == usuario_id)
    return consulta.order_by(Prestamo.fecha_prestamo.desc(), Prestamo.id.desc()).all()


@router.get("/mis-prestamos", response_model=list[PrestamoSalida], summary="Mis préstamos (usuario con sesión)")
def mis_prestamos(db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)):
    actualizar_vencidos(db)
    return (
        db.query(Prestamo)
        .filter(Prestamo.usuario_id == usuario.id)
        .order_by(Prestamo.fecha_prestamo.desc(), Prestamo.id.desc())
        .all()
    )


@router.get("/{prestamo_id}", response_model=PrestamoSalida, summary="Ver un préstamo (admin o dueño)")
def obtener(prestamo_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)):
    actualizar_vencidos(db)
    return buscar_prestamo(db, prestamo_id, usuario)


@router.post("", response_model=PrestamoSalida, status_code=201, summary="Pedir un libro prestado")
def crear(datos: PrestamoCrear, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)):
    """El **lector** pide el préstamo a su nombre.
    El **admin** puede indicar `usuario_id` para prestarle a otra persona.

    Reglas: el libro debe tener ejemplares disponibles, el usuario no puede tener
    el mismo libro sin devolver y máximo 3 préstamos sin devolver por usuario.
    """
    actualizar_vencidos(db)
    lector = usuario
    if usuario.rol == "admin" and datos.usuario_id:
        lector = db.get(Usuario, datos.usuario_id)
        if not lector:
            raise HTTPException(400, "El usuario indicado no existe")
        if not lector.activo:
            raise HTTPException(400, "El usuario indicado está inactivo")

    libro = db.get(Libro, datos.libro_id)
    if not libro:
        raise HTTPException(400, "El libro indicado no existe")
    if libro.ejemplares_disponibles <= 0:
        raise HTTPException(400, "No hay ejemplares disponibles de este libro")

    sin_devolver = db.query(Prestamo).filter(
        Prestamo.usuario_id == lector.id, Prestamo.estado.in_(SIN_DEVOLVER)
    )
    if sin_devolver.filter(Prestamo.libro_id == libro.id).first():
        raise HTTPException(400, "Este usuario ya tiene este libro prestado")
    if sin_devolver.count() >= MAX_PRESTAMOS_POR_USUARIO:
        raise HTTPException(400, f"Máximo {MAX_PRESTAMOS_POR_USUARIO} préstamos sin devolver por usuario")

    hoy = date.today()
    prestamo = Prestamo(
        usuario_id=lector.id,
        libro_id=libro.id,
        fecha_prestamo=hoy,
        fecha_limite=hoy + timedelta(days=datos.dias),
        estado="activo",
    )
    libro.ejemplares_disponibles -= 1
    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)
    return prestamo


@router.put("/{prestamo_id}", response_model=PrestamoSalida, summary="Cambiar fecha límite (admin)")
def actualizar(
    prestamo_id: int,
    datos: PrestamoActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(solo_admin),
):
    prestamo = buscar_prestamo(db, prestamo_id, usuario)
    if prestamo.estado == "devuelto":
        raise HTTPException(400, "El préstamo ya fue devuelto")
    if datos.fecha_limite < prestamo.fecha_prestamo:
        raise HTTPException(400, "La fecha límite no puede ser anterior a la fecha del préstamo")
    prestamo.fecha_limite = datos.fecha_limite
    prestamo.estado = "vencido" if datos.fecha_limite < date.today() else "activo"
    db.commit()
    db.refresh(prestamo)
    return prestamo


@router.put("/{prestamo_id}/devolver", response_model=PrestamoSalida, summary="Devolver un libro (admin o dueño)")
def devolver(prestamo_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)):
    prestamo = buscar_prestamo(db, prestamo_id, usuario)
    if prestamo.estado == "devuelto":
        raise HTTPException(400, "El préstamo ya fue devuelto")
    prestamo.estado = "devuelto"
    prestamo.fecha_devolucion = date.today()
    prestamo.libro.ejemplares_disponibles += 1
    db.commit()
    db.refresh(prestamo)
    return prestamo


@router.delete("/{prestamo_id}", response_model=Mensaje, summary="Eliminar préstamo (admin)")
def eliminar(prestamo_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(solo_admin)):
    prestamo = buscar_prestamo(db, prestamo_id, usuario)
    if prestamo.estado in SIN_DEVOLVER:
        prestamo.libro.ejemplares_disponibles += 1  # el ejemplar vuelve al inventario
    db.delete(prestamo)
    db.commit()
    return {"mensaje": "Préstamo eliminado"}
