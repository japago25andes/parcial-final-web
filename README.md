# Parcial Final · Programación Web

Este repositorio es el **backend** del parcial: una API REST de una **biblioteca** hecha con FastAPI y PostgreSQL, lista para usarse con Docker. Ya tiene datos y usuarios cargados.

## Qué debes hacer

1. **Levantar esta API** en tu computador con Docker.
2. **Construir un frontend en Angular** que la consuma. Puedes usar la IA que quieras. Las pantallas las decides tú.
3. **Desplegar toda la aplicación** (API + frontend) en una máquina virtual de Azure, configurándola por SSH.

## Qué debes mostrar el día del parcial

- El frontend funcionando en tu computador.
- La dirección pública de tu máquina en Azure (`http://IP-DE-TU-MAQUINA`) con la aplicación funcionando.
- Que hay avance y coherencia: debes poder explicar lo que hiciste.

---

## 1. Levantar la API en tu computador

Requisito: tener **Docker Desktop** instalado y abierto.

1. Descarga este repositorio con **Code → Download ZIP**, descomprímelo y renombra la carpeta a `api-biblioteca`.
2. Abre una terminal dentro de la carpeta y ejecuta:

   ```bash
   docker compose up -d --build
   ```

3. Abre **http://localhost:8080/docs**. Ahí está la documentación de todos los endpoints (Swagger).

La primera vez tarda un poco. Los datos se cargan solos.

## 2. Usuarios de prueba

| Rol | Correo | Contraseña |
|-----|--------|------------|
| admin | admin@biblioteca.com | admin123 |
| admin | bibliotecario@biblioteca.com | biblio123 |
| lector | lector@biblioteca.com | lector123 |
| lector | maria@correo.com | lector123 |
| lector | juan@correo.com | lector123 |
| lector | laura@correo.com | lector123 |
| lector (inactivo, no puede entrar) | andres@correo.com | lector123 |

- **admin**: puede hacer todo.
- **lector**: consulta el catálogo, pide préstamos y ve los suyos.

## 3. Probar la API en Swagger

1. En http://localhost:8080/docs pulsa **Authorize**.
2. Escribe un correo de la tabla y su contraseña.
3. Pulsa **Authorize** y **Close**.
4. Abre cualquier endpoint, pulsa **Try it out** y luego **Execute**.

## 4. Endpoints

**Público** = no necesita token. **Sesión** = cualquier usuario logueado. **Admin** = solo administradores.

| Método | Ruta | Acceso | Para qué sirve |
|--------|------|--------|----------------|
| POST | `/auth/login` | Público | Iniciar sesión. Devuelve el token |
| POST | `/auth/registro` | Público | Crear cuenta de lector |
| GET / PUT | `/auth/perfil` | Sesión | Ver o editar mi perfil |
| GET | `/libros` | Público | Listar libros. Filtros: `?buscar=`, `?autor_id=`, `?categoria_id=`, `?solo_disponibles=true` |
| GET | `/libros/{id}` | Público | Ver un libro |
| POST / PUT / DELETE | `/libros`, `/libros/{id}` | Admin | Crear, editar, eliminar libros |
| GET | `/autores`, `/autores/{id}` | Público | Listar (`?buscar=`) o ver autores |
| POST / PUT / DELETE | `/autores`, `/autores/{id}` | Admin | Crear, editar, eliminar autores |
| GET | `/categorias`, `/categorias/{id}` | Público | Listar o ver categorías |
| POST / PUT / DELETE | `/categorias`, `/categorias/{id}` | Admin | Crear, editar, eliminar categorías |
| POST | `/prestamos` | Sesión | Pedir un libro prestado |
| GET | `/prestamos/mis-prestamos` | Sesión | Mis préstamos |
| PUT | `/prestamos/{id}/devolver` | Sesión | Devolver un libro (admin o dueño del préstamo) |
| GET | `/prestamos` | Admin | Todos los préstamos. Filtros: `?estado=`, `?usuario_id=` |
| GET | `/prestamos/{id}` | Sesión | Ver un préstamo (admin o dueño) |
| PUT / DELETE | `/prestamos/{id}` | Admin | Cambiar fecha límite o eliminar |
| GET / POST / PUT / DELETE | `/usuarios`, `/usuarios/{id}` | Admin | Administrar usuarios |
| GET | `/estadisticas` | Admin | Totales y datos para un dashboard |

Los detalles de cada endpoint (qué enviar y qué responde) están en Swagger.

## 5. Conectar el frontend

- URL de la API en tu computador: `http://localhost:8080`
- URL de la API en Azure: `http://IP-DE-TU-MAQUINA:8080`

**Login:**

```http
POST /auth/login
Content-Type: application/json

{ "correo": "admin@biblioteca.com", "password": "admin123" }
```

Respuesta:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "usuario": { "id": 1, "nombre": "Administrador General", "correo": "admin@biblioteca.com", "rol": "admin", "activo": true }
}
```

En las peticiones que necesitan sesión envía el token en este header:

```
Authorization: Bearer eyJhbGciOi...
```

Si algo falla, la API responde con un mensaje en el campo `detail`, por ejemplo `{ "detail": "No hay ejemplares disponibles de este libro" }`.

CORS ya está abierto: el frontend puede llamar a la API desde cualquier dirección.

---

## 6. Despliegue en Azure

Todo se hace por **SSH**. En los ejemplos el usuario de la máquina es `azureuser`; cámbialo por el tuyo.

**1. Crea la máquina virtual** con Ubuntu Server y los puertos SSH (22), HTTP (80) y HTTPS (443). Luego, en **Redes** de la máquina, agrega una regla de entrada para el puerto **8080** (la API).

**2. Conéctate e instala Docker:**

```bash
ssh azureuser@IP-DE-TU-MAQUINA
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
exit
```

Vuelve a conectarte para que el cambio de permisos aplique.

**3. Sube la API.** Desde tu computador, en la carpeta donde está el proyecto:

```bash
scp -r ./api-biblioteca azureuser@IP-DE-TU-MAQUINA:~/api-biblioteca
```

Luego, dentro de la máquina:

```bash
cd ~/api-biblioteca
docker compose up -d --build
```

Revisa que abra `http://IP-DE-TU-MAQUINA:8080/docs`.

**4. Sube el frontend.** En tu proyecto Angular cambia la URL de la API por `http://IP-DE-TU-MAQUINA:8080` y publícalo en el puerto **80**. Lo más fácil es usar Docker (ejemplo abajo), pero puedes hacerlo como quieras. Lo importante es que funcione en `http://IP-DE-TU-MAQUINA`.

> Antes de copiar tu frontend con `scp`, **borra la carpeta `node_modules`**: pesa mucho y no se necesita.

<details>
<summary><b>Ejemplo: frontend Angular con Docker + nginx</b></summary>

Crea estos dos archivos en la raíz de tu proyecto Angular.

`Dockerfile` (cambia `NOMBRE-DE-TU-PROYECTO` por el nombre que aparece dentro de la carpeta `dist/` cuando ejecutas `ng build`):

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/NOMBRE-DE-TU-PROYECTO/browser /usr/share/nginx/html
EXPOSE 80
```

`nginx.conf`:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

En la máquina, dentro de la carpeta del frontend:

```bash
docker build -t frontend .
docker run -d --name frontend -p 80:80 --restart unless-stopped frontend
```

Para actualizarlo después de un cambio: `docker rm -f frontend`, luego repite los dos comandos anteriores.

</details>

---

## Comandos útiles

Ejecútalos dentro de la carpeta de la API:

| Comando | Qué hace |
|---------|----------|
| `docker compose ps` | Ver si los contenedores están corriendo |
| `docker compose logs -f api` | Ver los logs de la API |
| `docker compose down` | Detener la API |
| `docker compose down -v` y luego `docker compose up -d` | Borrar todo y volver a los datos iniciales |

## Problemas comunes

- **El puerto 8080 está ocupado en mi computador:** en `docker-compose.yml` cambia `"8080:8080"` por `"8081:8080"` y usa `http://localhost:8081`.
- **401 Unauthorized:** falta el token o expiró (dura 24 horas). Vuelve a iniciar sesión.
- **403 Forbidden:** tu usuario no tiene permiso, por ejemplo un lector intentando crear un libro.
- **En Azure no abre la página:** revisa la regla del puerto en **Redes** de la máquina y que los contenedores estén corriendo (`docker ps`).
- **`npm run build` falla en la máquina por falta de memoria:** compila en tu computador con `ng build` y sube solo la carpeta `dist` (en el `Dockerfile` del ejemplo quita la etapa de `node` y copia esa carpeta directamente).
- **Al recargar una ruta de Angular sale 404:** falta el `try_files` de `nginx.conf` del ejemplo.
