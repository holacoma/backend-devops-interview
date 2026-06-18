# Notas

Este proyecto aborda tres áreas del assignment: optimización del seeder, developer experience y production readiness. Las notas detalladas de cada área están en la carpeta `notes/`.

## Lo que se hizo

### Optimización del seeder
El seed original tardaba más de 10 minutos sin completar. Tras identificar los cuellos de botella mediante flamegraphs con `py-spy`, el tiempo se redujo a **56 segundos** para el dataset completo (1.000 users, 50 tags, 100.000 posts, 500.000 comments).

Ver detalle en [notes/optimizar_seeds.md](notes/optimizar_seeds.md).

### Developer experience
`docker compose up` levanta la app completa (PostgreSQL + Django) sin ninguna instalación local. Al arrancar con la base vacía, el entrypoint detecta los modelos sin datos y pregunta si se quiere seedear. La configuración de la DB es 100% configurable vía variables de entorno.

Ver detalle en [notes/developer_experience.md](notes/developer_experience.md). Tutorial de onboarding en [docs/tutorials/getting-started.md](docs/tutorials/getting-started.md).

### Production readiness
_(en progreso)_

## Qué deliberadamente no hice

- **Reproducibilidad exacta del seed** — al eliminar Faker se pierde la capacidad de reproducir el mismo contenido con `seed(42)`. La distribución de datos (power law, long tail) se preserva. Ver detalle en [notes/optimizar_seeds.md](notes/optimizar_seeds.md).
- **Ramas `develop` y `release`** — sin releases programados ni múltiples versiones en producción simultáneas, estas ramas agregan overhead sin beneficio real. Se trabaja con feature branches directamente contra `main`, integrados mediante PRs.

## Herramientas utilizadas

- **py-spy** — sampling profiler para flamegraphs. La herramienta más útil del proceso.
- **Claude Code** — utilizado para pair programming a lo largo del proyecto. Transcripción disponible bajo pedido.

