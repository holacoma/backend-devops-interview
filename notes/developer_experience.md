# Developer Experience — Notas

## Qué se hizo y por qué

El README original requería instalar `mise`, configurar PostgreSQL manualmente, editar `settings.py` para cambiar credenciales hardcodeadas, y conocer los comandos exactos de Django. El objetivo fue reducir ese proceso a un solo comando.

### Variables de entorno para la DB

`core/settings.py` tenía las credenciales de la base de datos hardcodeadas. Se movieron a variables de entorno (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`) con fallback a los valores estándar de Postgres. Esto permite configurar la conexión sin tocar el código y es prerequisito para cualquier setup con Docker.

### Makefile

Se agregó un `Makefile` con targets descriptivos para reemplazar los comandos `manage.py` directos:

| Target            | Qué hace                                      |
|-------------------|-----------------------------------------------|
| `make setup`      | Instala dependencias y crea la base de datos  |
| `make migrate`    | Aplica migraciones pendientes                 |
| `make migrate-check` | Verifica si hay migraciones sin aplicar    |
| `make server`     | Levanta el servidor de desarrollo             |

### Script de setup (`setup.sh`)

Script bash que detecta el OS (macOS via Homebrew, Linux via apt), instala `uv` y PostgreSQL si no están disponibles, y crea la base de datos. Saltea lo que ya esté instalado.

### Docker Compose

`docker compose up` levanta la app completa (PostgreSQL 17 + Django) sin ninguna instalación local. El entrypoint (`entrypoint.sh`) detecta los modelos sin datos al arrancar y pregunta si se quiere seedear antes de levantar el servidor. La escala del seed es configurable via `SEED_SCALE` (default `0.1` = ~10% del dataset).

## Documentación

El tutorial de onboarding sigue el paradigma Diátaxis en `docs/tutorials/getting-started.md`.
