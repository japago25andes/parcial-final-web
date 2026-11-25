from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Autor
from app.schemas import AutorActualizar, AutorCrear, AutorSalida, Mensaje
from app.seguridad import solo_admin

router = APIRouter(prefix="/autores", tags=["Autores"])


def buscar_autor(db: Session, autor_id: int) -> Autor:
    autor = db.get(Autor, autor_id)
    if not autor:
        raise HTTPException(404, "Autor no encontrado")
    return autor


@router.get("", response_model=list[AutorSalida], summary="Listar autores (público)")
def listar(buscar: str | None = None, db: Session = Depends(get_db)):
    """`buscar` filtra por nombre o nacionalidad."""
    consulta = db.query(Autor)
    if buscar:
        consulta = consulta.filter(
            Autor.nombre.ilike(f"%{buscar}%") | Autor.nacionalidad.ilike(f"%{buscar}%")
        )
    return consulta.order_by(Autor.nombre).all()


@router.get("/{autor_id}", response_model=AutorSalida, summary="Ver un autor (público)")
def obtener(autor_id: int, db: Session = Depends(get_db)):
    return buscar_autor(db, autor_id)


@router.post("", response_model=AutorSalida, status_code=201, summary="Crear autor (admin)")
def crear(datos: AutorCrear, db: Session = Depends(get_db), _=Depends(solo_admin)):
    autor = Autor(**datos.model_dump())
    db.add(autor)
    db.commit()
    db.refresh(autor)
    return autor


@router.put("/{autor_id}", response_model=AutorSalida, summary="Actualizar autor (admin)")
def actualizar(autor_id: int, datos: AutorActualizar, db: Session = Depends(get_db), _=Depends(solo_admin)):
    autor = buscar_autor(db, autor_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(autor, campo, valor)
    db.commit()
    db.refresh(autor)
    return autor


@router.delete("/{autor_id}", response_model=Mensaje, summary="Eliminar autor (admin)")
def eliminar(autor_id: int, db: Session = Depends(get_db), _=Depends(solo_admin)):
    autor = buscar_autor(db, autor_id)
    if autor.libros:
        raise HTTPException(400, "No se puede eliminar: el autor tiene libros registrados")
    db.delete(autor)
    db.commit()
    return {"mensaje": "Autor eliminado"}
