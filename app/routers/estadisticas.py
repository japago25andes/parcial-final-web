from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Autor, Categoria, Libro, Prestamo, Usuario
from app.routers.prestamos import actualizar_vencidos
from app.seguridad import solo_admin

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])


@router.get("", summary="Resumen para un dashboard (admin)")
def resumen(db: Session = Depends(get_db), _=Depends(solo_admin)):
    """Totales generales, préstamos por estado, libros más prestados y libros por categoría."""
    actualizar_vencidos(db)

    def contar_prestamos(estado: str) -> int:
        return db.query(Prestamo).filter(Prestamo.estado == estado).count()

    mas_prestados = (
        db.query(Libro.id, Libro.titulo, Libro.portada_url, func.count(Prestamo.id).label("total"))
        .join(Prestamo, Prestamo.libro_id == Libro.id)
        .group_by(Libro.id)
        .order_by(func.count(Prestamo.id).desc(), Libro.titulo)
        .limit(5)
        .all()
    )
    por_categoria = (
        db.query(Categoria.nombre, func.count(Libro.id))
        .outerjoin(Libro, Libro.categoria_id == Categoria.id)
        .group_by(Categoria.id)
        .order_by(Categoria.nombre)
        .all()
    )

    return {
        "total_libros": db.query(Libro).count(),
        "total_ejemplares": db.query(func.coalesce(func.sum(Libro.ejemplares_totales), 0)).scalar(),
        "ejemplares_disponibles": db.query(func.coalesce(func.sum(Libro.ejemplares_disponibles), 0)).scalar(),
        "total_autores": db.query(Autor).count(),
        "total_categorias": db.query(Categoria).count(),
        "total_usuarios": db.query(Usuario).count(),
        "prestamos_activos": contar_prestamos("activo"),
        "prestamos_vencidos": contar_prestamos("vencido"),
        "prestamos_devueltos": contar_prestamos("devuelto"),
        "libros_mas_prestados": [
            {"id": l.id, "titulo": l.titulo, "portada_url": l.portada_url, "total_prestamos": l.total}
            for l in mas_prestados
        ],
        "libros_por_categoria": [{"categoria": nombre, "total_libros": total} for nombre, total in por_categoria],
    }
