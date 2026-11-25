"""Esquemas (Pydantic): definen qué datos entran y salen de cada endpoint."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class Esquema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Autenticación ----------

class LoginEntrada(BaseModel):
    correo: str = Field(examples=["admin@biblioteca.com"])
    password: str = Field(examples=["admin123"])


class RegistroEntrada(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, examples=["Nuevo Lector"])
    correo: str = Field(pattern=CORREO, max_length=120, examples=["nuevo@correo.com"])
    password: str = Field(min_length=6, max_length=50, examples=["clave123"])


class PerfilActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    password: str | None = Field(default=None, min_length=6, max_length=50)


# ---------- Usuarios ----------

class UsuarioSalida(Esquema):
    id: int
    nombre: str
    correo: str
    rol: str
    activo: bool
    fecha_registro: datetime


class UsuarioResumen(Esquema):
    id: int
    nombre: str
    correo: str


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, examples=["Pedro Ramírez"])
    correo: str = Field(pattern=CORREO, max_length=120, examples=["pedro@correo.com"])
    password: str = Field(min_length=6, max_length=50, examples=["clave123"])
    rol: Literal["admin", "lector"] = "lector"
    activo: bool = True


class UsuarioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    correo: str | None = Field(default=None, pattern=CORREO, max_length=120)
    password: str | None = Field(default=None, min_length=6, max_length=50)
    rol: Literal["admin", "lector"] | None = None
    activo: bool | None = None


class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioSalida


# ---------- Autores ----------

class AutorCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=120, examples=["Laura Restrepo"])
    nacionalidad: str | None = Field(default=None, max_length=60, examples=["Colombiana"])
    fecha_nacimiento: date | None = Field(default=None, examples=["1950-01-01"])
    biografia: str | None = Field(default=None, examples=["Escritora y periodista colombiana."])


class AutorActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    nacionalidad: str | None = Field(default=None, max_length=60)
    fecha_nacimiento: date | None = None
    biografia: str | None = None


class AutorSalida(Esquema):
    id: int
    nombre: str
    nacionalidad: str | None
    fecha_nacimiento: date | None
    biografia: str | None
    total_libros: int = 0


class AutorResumen(Esquema):
    id: int
    nombre: str


# ---------- Categorías ----------

class CategoriaCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=80, examples=["Poesía"])
    descripcion: str | None = Field(default=None, examples=["Obras escritas en verso."])


class CategoriaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    descripcion: str | None = None


class CategoriaSalida(Esquema):
    id: int
    nombre: str
    descripcion: str | None
    total_libros: int = 0


class CategoriaResumen(Esquema):
    id: int
    nombre: str


# ---------- Libros ----------

class LibroCrear(BaseModel):
    titulo: str = Field(min_length=1, max_length=200, examples=["Delirio"])
    isbn: str = Field(min_length=5, max_length=20, examples=["9789584203410"])
    anio_publicacion: int | None = Field(default=None, examples=[2004])
    paginas: int | None = Field(default=None, ge=1, examples=[350])
    sinopsis: str | None = Field(default=None, examples=["Una mujer enloquece y su esposo intenta descubrir por qué."])
    portada_url: str | None = Field(default=None, max_length=300, examples=["https://placehold.co/300x450?text=Delirio"])
    ejemplares_totales: int = Field(default=1, ge=0, examples=[3])
    autor_id: int = Field(examples=[1])
    categoria_id: int = Field(examples=[1])


class LibroActualizar(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    isbn: str | None = Field(default=None, min_length=5, max_length=20)
    anio_publicacion: int | None = None
    paginas: int | None = Field(default=None, ge=1)
    sinopsis: str | None = None
    portada_url: str | None = Field(default=None, max_length=300)
    ejemplares_totales: int | None = Field(default=None, ge=0)
    autor_id: int | None = None
    categoria_id: int | None = None


class LibroSalida(Esquema):
    id: int
    titulo: str
    isbn: str
    anio_publicacion: int | None
    paginas: int | None
    sinopsis: str | None
    portada_url: str | None
    ejemplares_totales: int
    ejemplares_disponibles: int
    autor: AutorResumen
    categoria: CategoriaResumen


class LibroResumen(Esquema):
    id: int
    titulo: str
    portada_url: str | None


# ---------- Préstamos ----------

class PrestamoCrear(BaseModel):
    libro_id: int = Field(examples=[1])
    usuario_id: int | None = Field(
        default=None,
        description="Solo lo usa el admin para prestarle a otro usuario. El lector siempre presta a su nombre.",
        examples=[None],
    )
    dias: int = Field(default=14, ge=1, le=60, description="Días de préstamo (1 a 60)")


class PrestamoActualizar(BaseModel):
    fecha_limite: date = Field(description="Nueva fecha límite de devolución", examples=["2030-01-31"])


class PrestamoSalida(Esquema):
    id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: date | None
    estado: str
    usuario: UsuarioResumen
    libro: LibroResumen


# ---------- Otros ----------

class Mensaje(BaseModel):
    mensaje: str
