"""Punto de entrada de la API de la Biblioteca."""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.routers import auth, autores, categorias, estadisticas, libros, prestamos, usuarios
from app.seed import cargar_datos_iniciales

DESCRIPCION = """
API REST de una **biblioteca** para el Parcial Final de Programación Web.

### Cómo probarla aquí mismo
1. Pulsa el botón **Authorize** (arriba a la derecha).
2. Escribe uno de los correos de la tabla y su contraseña.
3. Pulsa **Authorize** y luego **Close**. Ya puedes usar todos los endpoints con ese usuario.

### Usuarios de prueba
| Rol | Correo | Contraseña |
|-----|--------|------------|
| admin | admin@biblioteca.com | admin123 |
| admin | bibliotecario@biblioteca.com | biblio123 |
| lector | lector@biblioteca.com | lector123 |
| lector | maria@correo.com | lector123 |
| lector | juan@correo.com | lector123 |
| lector | laura@correo.com | lector123 |
| lector (inactivo, no puede entrar) | andres@correo.com | lector123 |

### Desde el frontend
Inicia sesión con `POST /auth/login` y envía el token en cada petición con el header
`Authorization: Bearer <access_token>`.
"""

ETIQUETAS = [
    {"name": "Autenticación", "description": "Login, registro y perfil del usuario con sesión."},
    {"name": "Libros", "description": "Consultar es público. Crear, editar y eliminar es solo para admin."},
    {"name": "Autores", "description": "Consultar es público. Crear, editar y eliminar es solo para admin."},
    {"name": "Categorías", "description": "Consultar es público. Crear, editar y eliminar es solo para admin."},
    {"name": "Préstamos", "description": "Requieren sesión. El lector maneja sus préstamos; el admin, todos."},
    {"name": "Usuarios", "description": "Administración de usuarios (solo admin)."},
    {"name": "Estadísticas", "description": "Datos para un dashboard (solo admin)."},
]


def esperar_base_de_datos(intentos: int = 30):
    """Al arrancar con Docker, la base de datos puede tardar unos segundos en estar lista."""
    for _ in range(intentos):
        try:
            with engine.connect() as conexion:
                conexion.execute(text("SELECT 1"))
            return
        except Exception:
            print("Esperando a la base de datos...")
            time.sleep(2)
    raise RuntimeError("No fue posible conectarse a la base de datos")


@asynccontextmanager
async def lifespan(app: FastAPI):
    esperar_base_de_datos()
    Base.metadata.create_all(bind=engine)  # crea las tablas si no existen
    with SessionLocal() as db:
        cargar_datos_iniciales(db)
    yield


app = FastAPI(
    title="API Biblioteca · Parcial Final Programación Web",
    description=DESCRIPCION,
    version="1.0.0",
    openapi_tags=ETIQUETAS,
    lifespan=lifespan,
    docs_url=None,  # /docs se define abajo para simplificar el login de Swagger
    swagger_ui_parameters={"persistAuthorization": True},
)

# Oculta los campos de OAuth2 que esta API no usa (client_id, client_secret, scopes)
# para que el botón Authorize pida solo correo y contraseña.
ESTILO_SWAGGER = """
.auth-container .scope-def,
.auth-container .flow,
.auth-container .wrapper:has(> label[for="password_type"]),
.auth-container .wrapper:has(> label[for="client_id_password"]),
.auth-container .wrapper:has(> label[for="client_secret_password"]) { display: none; }
label[for="oauth_username"], label[for="oauth_password"] { font-size: 0; }
label[for="oauth_username"]::after { content: "Correo:"; font-size: 12px; }
label[for="oauth_password"]::after { content: "Contraseña:"; font-size: 12px; }
"""


@app.get("/docs", include_in_schema=False)
def documentacion():
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_ui_parameters=app.swagger_ui_parameters,
    ).body.decode()
    return HTMLResponse(html.replace("</head>", f"<style>{ESTILO_SWAGGER}</style></head>"))

# CORS abierto: permite que cualquier frontend (localhost:4200, la IP de la máquina, etc.) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(libros.router)
app.include_router(autores.router)
app.include_router(categorias.router)
app.include_router(prestamos.router)
app.include_router(usuarios.router)
app.include_router(estadisticas.router)


@app.get("/", tags=["Inicio"], summary="Verificar que la API está funcionando")
def inicio():
    return {"mensaje": "API Biblioteca funcionando", "documentacion": "/docs"}
