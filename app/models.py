"""Tablas de la base de datos."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    rol: Mapped[str] = mapped_column(String(20), default="lector")  # "admin" o "lector"
    activo: Mapped[bool] = mapped_column(default=True)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    prestamos: Mapped[list["Prestamo"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


class Autor(Base):
    __tablename__ = "autores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    nacionalidad: Mapped[str | None] = mapped_column(String(60))
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date)
    biografia: Mapped[str | None] = mapped_column(Text)

    libros: Mapped[list["Libro"]] = relationship(back_populates="autor")

    @property
    def total_libros(self) -> int:
        return len(self.libros)


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text)

    libros: Mapped[list["Libro"]] = relationship(back_populates="categoria")

    @property
    def total_libros(self) -> int:
        return len(self.libros)


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    isbn: Mapped[str] = mapped_column(String(20), unique=True)
    anio_publicacion: Mapped[int | None]
    paginas: Mapped[int | None]
    sinopsis: Mapped[str | None] = mapped_column(Text)
    portada_url: Mapped[str | None] = mapped_column(String(300))
    ejemplares_totales: Mapped[int] = mapped_column(default=1)
    ejemplares_disponibles: Mapped[int] = mapped_column(default=1)
    autor_id: Mapped[int] = mapped_column(ForeignKey("autores.id"))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))

    autor: Mapped[Autor] = relationship(back_populates="libros")
    categoria: Mapped[Categoria] = relationship(back_populates="libros")
    prestamos: Mapped[list["Prestamo"]] = relationship(
        back_populates="libro", cascade="all, delete-orphan"
    )


class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    libro_id: Mapped[int] = mapped_column(ForeignKey("libros.id"))
    fecha_prestamo: Mapped[date] = mapped_column(Date)
    fecha_limite: Mapped[date] = mapped_column(Date)
    fecha_devolucion: Mapped[date | None] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="activo")  # activo, vencido, devuelto

    usuario: Mapped[Usuario] = relationship(back_populates="prestamos")
    libro: Mapped[Libro] = relationship(back_populates="prestamos")
