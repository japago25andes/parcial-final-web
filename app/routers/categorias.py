from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Categoria
from app.schemas import CategoriaActualizar, CategoriaCrear, CategoriaSalida, Mensaje
from app.seguridad import solo_admin

router = APIRouter(prefix="/categorias", tags=["Categorías"])


def buscar_categoria(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(404, "Categoría no encontrada")
    return categoria


def validar_nombre_unico(db: Session, nombre: str, excluir_id: int | None = None):
    consulta = db.query(Categoria).filter(func.lower(Categoria.nombre) == nombre.strip().lower())
    if excluir_id:
        consulta = consulta.filter(Categoria.id != excluir_id)
    if consulta.first():
        raise HTTPException(400, "Ya existe una categoría con ese nombre")


@router.get("", response_model=list[CategoriaSalida], summary="Listar categorías (público)")
def listar(db: Session = Depends(get_db)):
    return db.query(Categoria).order_by(Categoria.nombre).all()


@router.get("/{categoria_id}", response_model=CategoriaSalida, summary="Ver una categoría (público)")
def obtener(categoria_id: int, db: Session = Depends(get_db)):
    return buscar_categoria(db, categoria_id)


@router.post("", response_model=CategoriaSalida, status_code=201, summary="Crear categoría (admin)")
def crear(datos: CategoriaCrear, db: Session = Depends(get_db), _=Depends(solo_admin)):
    validar_nombre_unico(db, datos.nombre)
    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaSalida, summary="Actualizar categoría (admin)")
def actualizar(
    categoria_id: int, datos: CategoriaActualizar, db: Session = Depends(get_db), _=Depends(solo_admin)
):
    categoria = buscar_categoria(db, categoria_id)
    if datos.nombre:
        validar_nombre_unico(db, datos.nombre, excluir_id=categoria_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", response_model=Mensaje, summary="Eliminar categoría (admin)")
def eliminar(categoria_id: int, db: Session = Depends(get_db), _=Depends(solo_admin)):
    categoria = buscar_categoria(db, categoria_id)
    if categoria.libros:
        raise HTTPException(400, "No se puede eliminar: la categoría tiene libros registrados")
    db.delete(categoria)
    db.commit()
    return {"mensaje": "Categoría eliminada"}
