from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Autor, Categoria, Libro, Prestamo
from app.schemas import LibroActualizar, LibroCrear, LibroSalida, Mensaje
from app.seguridad import solo_admin

router = APIRouter(prefix="/libros", tags=["Libros"])


def buscar_libro(db: Session, libro_id: int) -> Libro:
    libro = db.get(Libro, libro_id)
    if not libro:
        raise HTTPException(404, "Libro no encontrado")
    return libro


def validar_relaciones(db: Session, autor_id: int | None, categoria_id: int | None):
    if autor_id is not None and not db.get(Autor, autor_id):
        raise HTTPException(400, "El autor indicado no existe")
    if categoria_id is not None and not db.get(Categoria, categoria_id):
        raise HTTPException(400, "La categoría indicada no existe")


def validar_isbn_unico(db: Session, isbn: str, excluir_id: int | None = None):
    consulta = db.query(Libro).filter(Libro.isbn == isbn)
    if excluir_id:
        consulta = consulta.filter(Libro.id != excluir_id)
    if consulta.first():
        raise HTTPException(400, "Ya existe un libro con ese ISBN")


def prestamos_sin_devolver(db: Session, libro_id: int) -> int:
    return (
        db.query(Prestamo)
        .filter(Prestamo.libro_id == libro_id, Prestamo.estado.in_(["activo", "vencido"]))
        .count()
    )


@router.get("", response_model=list[LibroSalida], summary="Listar libros (público)")
def listar(
    buscar: str | None = None,
    autor_id: int | None = None,
    categoria_id: int | None = None,
    solo_disponibles: bool = False,
    db: Session = Depends(get_db),
):
    """Filtros opcionales:

    - `buscar`: texto en el título, ISBN o nombre del autor
    - `autor_id` / `categoria_id`: libros de un autor o de una categoría
    - `solo_disponibles=true`: solo libros con ejemplares disponibles
    """
    consulta = db.query(Libro).join(Libro.autor)
    if buscar:
        texto = f"%{buscar}%"
        consulta = consulta.filter(
            Libro.titulo.ilike(texto) | Libro.isbn.ilike(texto) | Autor.nombre.ilike(texto)
        )
    if autor_id:
        consulta = consulta.filter(Libro.autor_id == autor_id)
    if categoria_id:
        consulta = consulta.filter(Libro.categoria_id == categoria_id)
    if solo_disponibles:
        consulta = consulta.filter(Libro.ejemplares_disponibles > 0)
    return consulta.order_by(Libro.titulo).all()


@router.get("/{libro_id}", response_model=LibroSalida, summary="Ver un libro (público)")
def obtener(libro_id: int, db: Session = Depends(get_db)):
    return buscar_libro(db, libro_id)


@router.post("", response_model=LibroSalida, status_code=201, summary="Crear libro (admin)")
def crear(datos: LibroCrear, db: Session = Depends(get_db), _=Depends(solo_admin)):
    validar_relaciones(db, datos.autor_id, datos.categoria_id)
    validar_isbn_unico(db, datos.isbn)
    libro = Libro(**datos.model_dump(), ejemplares_disponibles=datos.ejemplares_totales)
    db.add(libro)
    db.commit()
    db.refresh(libro)
    return libro


@router.put("/{libro_id}", response_model=LibroSalida, summary="Actualizar libro (admin)")
def actualizar(libro_id: int, datos: LibroActualizar, db: Session = Depends(get_db), _=Depends(solo_admin)):
    libro = buscar_libro(db, libro_id)
    cambios = datos.model_dump(exclude_unset=True)
    validar_relaciones(db, cambios.get("autor_id"), cambios.get("categoria_id"))
    if cambios.get("isbn"):
        validar_isbn_unico(db, cambios["isbn"], excluir_id=libro_id)

    # Si cambia el total de ejemplares, se recalculan los disponibles
    if cambios.get("ejemplares_totales") is not None:
        prestados = prestamos_sin_devolver(db, libro_id)
        if cambios["ejemplares_totales"] < prestados:
            raise HTTPException(400, f"No puede haber menos de {prestados} ejemplares: están prestados")
        libro.ejemplares_disponibles = cambios["ejemplares_totales"] - prestados

    for campo, valor in cambios.items():
        if valor is not None:
            setattr(libro, campo, valor)
    db.commit()
    db.refresh(libro)
    return libro


@router.delete("/{libro_id}", response_model=Mensaje, summary="Eliminar libro (admin)")
def eliminar(libro_id: int, db: Session = Depends(get_db), _=Depends(solo_admin)):
    libro = buscar_libro(db, libro_id)
    if prestamos_sin_devolver(db, libro_id):
        raise HTTPException(400, "No se puede eliminar: el libro tiene préstamos sin devolver")
    db.delete(libro)  # también borra su historial de préstamos
    db.commit()
    return {"mensaje": "Libro eliminado"}
