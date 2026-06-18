# Notas

Este proyecto aborda tres áreas del assignment: optimización del seeder, developer experience y performance de endpoints. Las notas detalladas de cada área están en la carpeta `notes/`.

## Lo que se hizo

### Optimización del seeder
El seed original tardaba más de 10 minutos sin completar. Tras identificar los cuellos de botella mediante flamegraphs con `py-spy`, el tiempo se redujo a **56 segundos** para el dataset completo (1.000 users, 50 tags, 100.000 posts, 500.000 comments).

Ver detalle en [notes/optimizar_seeds.md](notes/optimizar_seeds.md).

### Developer experience
`docker compose up` levanta la app completa (PostgreSQL + Django) sin ninguna instalación local. Al arrancar con la base vacía, el entrypoint detecta los modelos sin datos y pregunta si se quiere seedear. La configuración de la DB es 100% configurable vía variables de entorno.

Ver detalle en [notes/developer_experience.md](notes/developer_experience.md). Tutorial de onboarding en [docs/tutorials/getting-started.md](docs/tutorials/getting-started.md).

### Performance

Los cuatro endpoints de posts tenían N+1 queries: `_serialize_post_list` accedía a `post.author` (FK) y `post.tags` (M2M) sin prefetch, disparando un query extra por post por relación. Se eliminaron con `select_related("author")` y `prefetch_related("tags")` de forma consistente en todos los endpoints afectados. Además se agregó paginación a `GET /api/posts` — sin ella, el endpoint daba timeout con el dataset completo. Medición y diagnóstico con `django-silk`.

| Endpoint | Queries antes | Queries después | Tiempo antes | Tiempo después |
|---|---|---|---|---|
| `GET /api/posts` | 1821 | 2 | 1919ms | 47ms |
| `GET /api/posts/by-tag/{slug}` | 1534 | 3 | 4280ms | 110ms |
| `GET /api/posts/{id}` | 217 | 4 | 351ms | 24ms |
| `GET /api/posts/search` | 1821 | 2 | 1851ms | 127ms |

Ver detalle en [notes/performance.md](notes/performance.md).

## Qué deliberadamente no hice

- **Reproducibilidad exacta del seed** — al eliminar Faker se pierde la capacidad de reproducir el mismo contenido con `seed(42)`. La distribución de datos (power law, long tail) se preserva. Ver detalle en [notes/optimizar_seeds.md](notes/optimizar_seeds.md).
- **Ramas `develop` y `release`** — sin releases programados ni múltiples versiones en producción simultáneas, estas ramas agregan overhead sin beneficio real. Se trabaja con feature branches directamente contra `main`, integrados mediante PRs.
- **Índice GIN para búsqueda full-text** — `search_posts` usa `icontains` que traduce a `LIKE '%q%'`, seq scan sin índice. Con 1k posts el cuello de botella era el N+1; con el dataset completo sería el siguiente problema. Requeriría `pg_trgm` o `SearchVector`/`SearchQuery` de `django.contrib.postgres`.
- **N+1 en `_user_detail`** — `get_user` y `find_user_by_email` hacen dos `COUNT` separados. El fix es trivial (`annotate`), pero el endpoint no aparecía en los más lentos con el dataset de prueba.
- **Endpoints de creación masiva** — `POST /api/posts` y `POST /api/posts/{id}/comments` no se analizaron en profundidad. A escala, reemplazar N requests individuales por un `bulk_create` único reduce significativamente el costo de escritura.

## Qué haría con otro día

- **Tests de happy path por endpoint** — el proyecto tiene smoke tests pero no cubre los endpoints individualmente. Agregaría un test por endpoint con el caso feliz: status 200, shape del response, y al menos una assertion sobre los datos. Base mínima para CI útil.
- **Deploy completo** — Docker Compose está listo para desarrollo local. El siguiente paso es llevar eso a producción: un Dockerfile de producción (sin dev deps, sin DEBUG), variables de entorno desde secrets, y un target concreto (Fly.io, Render, o ECS). El esqueleto está; falta el último tramo.
- **Benchmark automático de endpoints** — un script que corra contra la DB con datos reales, mida tiempo y conteo de queries por endpoint, y genere un reporte. Permite detectar regresiones antes de que lleguen a producción y tiene el output listo para convertir en tickets (Jira, Linear, lo que sea).
- **Refactorizar `blog/api.py`** — el controller mezcla serialización, lógica de negocio y acceso a datos en el mismo archivo. Separaría los serializers en `schemas.py` (ya existe parcialmente), la lógica de queries en un módulo de servicios o repositorio, y dejaría los handlers lo más delgados posible.
- **Documentación automática de modelos** — agregar `django-extensions` con `graph_models` para generar un diagrama ER desde los modelos, o `drf-spectacular` si se migrara a DRF. Con Ninja, el OpenAPI ya está en `/api/docs`; lo que falta es el diagrama de base de datos para onboarding.

## Herramientas utilizadas

- **py-spy** — sampling profiler para flamegraphs. La herramienta más útil del proceso.
- **django-silk** — middleware de profiling para requests HTTP. Registra queries SQL, tiempos y planes de ejecución por request; disponible en `/silk/` en modo DEBUG.
- **Claude Code** — utilizado para pair programming a lo largo del proyecto. Transcripción disponible bajo pedido.

