# Tutorial: levanta la app por primera vez

Dos caminos según lo que tengas disponible: con Docker (sin instalar nada más) o directo en tu máquina.

---

## Opción A — con Docker

No requiere instalar PostgreSQL ni Python. Solo necesitas [Docker](https://docs.docker.com/get-docker/) con el plugin Compose (Docker Desktop ya lo trae).

### 1. Clona el repositorio

```sh
git clone <url-del-repo>
cd backend-devops-interview
```

### 2. Levanta la app

```sh
docker compose up
```

Docker va a:
1. Descargar la imagen de PostgreSQL 17
2. Construir la imagen de la aplicación instalando las dependencias con `uv`
3. Esperar a que la base de datos esté lista
4. Correr las migraciones automáticamente

### 3. Decide si quieres datos de prueba

Cuando la base de datos esté vacía, el terminal te pregunta:

```
Missing data detected:
  Users:    0
  Tags:     0
  Posts:    0
  Comments: 0

Seed the database? [y/N]
```

Responde `y` si quieres explorar la API con datos reales. El seed carga ~10% del dataset completo (~100 usuarios, ~10.000 posts, ~50.000 comentarios) y tarda un par de minutos.

### 4. Abre la API

Una vez que ves `Starting development server at http://0.0.0.0:8000/`, la API está lista en:

```
http://localhost:8000/api/docs
```

Desde ahí puedes explorar todos los endpoints de forma interactiva.

> Si el puerto 8000 ya está en uso, podés cambiarlo sin tocar el archivo:
> ```sh
> APP_PORT=9000 docker compose up
> ```

---

## Opción B — local (sin Docker)

### 1. Clona el repositorio

```sh
git clone <url-del-repo>
cd backend-devops-interview
```

### 2. Instala dependencias y prepara la base de datos

```sh
make setup
```

`make setup` detecta tu OS automáticamente (macOS via Homebrew, Linux via apt) e instala `uv` y PostgreSQL si no los tenés. También crea la base de datos. Saltea lo que ya esté instalado.

### 3. Corre las migraciones

```sh
make migrate
```

### 4. Levanta el servidor

```sh
make server
```

La API está lista en `http://localhost:8000/api/docs`.
