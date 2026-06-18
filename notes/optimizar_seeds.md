# Notas

## Qué hice y por qué

### 1. Refactor: separar el seed command en seeders por modelo

El `seed.py` original tenía un método `handle()` de ~100 líneas mezclando la lógica de seed de los 4 modelos. Es un Long Method clásico — difícil de leer, difícil de testear e imposible de hacer benchmark en aislamiento.

Extraje cada modelo en su propio módulo bajo `blog/management/commands/seeders/`:

```
seeders/
    utils.py      ← helpers compartidos (random_time, funciones de peso)
    users.py      ← seed_users()
    tags.py       ← seed_tags()
    posts.py      ← seed_posts() + attach_post_tags()
    comments.py   ← seed_comments()
```

`seed.py` ahora solo orquesta el flujo. Esto sigue el principio de Responsabilidad Única y hace que cada seeder sea legible y debuggeable de forma independiente.

También agregué `blog/factories.py` usando `factory_boy`, que es el patrón estándar en proyectos Django para generar instancias de modelos en tests y seeds.

### 2. Nuevos parámetros de entrada en el seed command

El seed original solo aceptaba `--force` para saltear el chequeo de datos existentes, sin ninguna forma de controlar el volumen ni de limpiar la DB.

Se agregaron dos flags:

**`--scale <float>`** — seedea una fracción del dataset completo (ej: `--scale 0.05` = 5%). Fue clave para el proceso de benchmarking: permite iterar rápido sobre el profiler sin esperar minutos por un seed completo. Los volúmenes escalan proporcionalmente manteniendo las mismas distribuciones (power law de autores, long tail de comments).

```sh
uv run python manage.py seed --scale 0.05   # 50 users, 6 tags, 5.000 posts, 25.000 comments
uv run python manage.py seed                 # dataset completo
```

**`--purge`** — elimina todos los datos existentes antes de seedear (users, tags, posts, comments en orden para respetar FK constraints). Se mantuvo separado de `--force` deliberadamente: `--force` solo saltea el chequeo, `--purge` destruye datos. Combinarlos habría creado un flag con dos responsabilidades y riesgo de pérdida accidental de datos.

```sh
uv run python manage.py seed --purge --scale 0.05   # limpia y reseedea
```

### 3. Fixes de performance encontrados via flamegraph

Se usó `py-spy` para generar flamegraphs en speedscope en cada iteración. Tres cuellos de botella aparecieron en orden:

**Fix 1 — Generación de texto con Faker en posts (era el 80% del tiempo)**

`posts.py` llamaba a `fake.text()` y `fake.sentence()` 10.000 veces cada uno para construir pools de títulos y cuerpos, antes de insertar una sola fila. Faker construye texto realista palabra por palabra desde listas internas — lento por diseño. Para datos de seed, el contenido no necesita ser realista.

Se reemplazó con f-strings simples:
```python
# antes
title_pool = [fake.sentence(nb_words=8).rstrip(".") for _ in range(10_000)]
body_pool  = [fake.text(max_nb_chars=600) for _ in range(10_000)]

# después
title_pool = [f"Post title {i}" for i in range(TITLE_POOL_SIZE)]
body_pool  = [f"Post body {i}"  for i in range(BODY_POOL_SIZE)]
```

El mismo fix se aplicó a `comments.py`, donde `fake.sentence()` se llamaba una vez por comment (500.000 veces a escala completa).

**Fix 2 — `random.choices(k=1)` dentro del loop de comments (era el 70% después del fix 1)**

`random.choices()` con argumento `weights` reconstruye la suma acumulada de pesos en cada llamada. Llamado con `k=1` dentro de un loop de 500.000 iteraciones sobre una lista de 100.000 post IDs, esto equivale a ~50 billones de operaciones de suma acumulada.

Mover la llamada fuera del loop interno con `k=chunk_size` lo reduce a un cómputo de suma acumulada por batch:
```python
# antes: 500.000 llamadas × suma acumulada de 100.000 elementos cada una
for _ in range(num_comments):
    pid = random.choices(post_ids, weights=post_weights, k=1)[0]

# después: 500 llamadas × suma acumulada de 100.000 elementos cada una
chunk_post_ids   = random.choices(post_ids, weights=post_weights,  k=chunk_size)
chunk_author_ids = random.choices(user_ids, weights=author_weights, k=chunk_size)
```

**Fix 3 — `transaction.atomic()` faltante en comments (era el 35% después del fix 2)**

Sin una transacción explícita, cada `bulk_create` es su propio auto-commit. PostgreSQL con `synchronous_commit=on` (el default) llama a `fsync()` después de cada commit, esperando que el WAL se escriba durablemente en disco. Con 500 batches de 1.000 comments, esto se acumula significativamente.

Envolver cada batch en `transaction.atomic()` reduce los fsyncs a uno por commit de batch.

## Qué deliberadamente no hice

- **Modificar el domain model** — la relación ManyToMany entre Post y Tag es diseño relacional correcto. Un ArrayField en Post simplificaría el seed pero desnormaliza el esquema para un beneficio que no es determinante acá.
- **Fix de `random.choices(k=1)` en `posts.py`** — el mismo problema existe en el seeder de posts. Con 100.000 posts y una lista de 1.000 usuarios el impacto es mucho menor que en comments (100M vs 50B operaciones), por lo que el flamegraph no lo priorizó dentro del tiempo disponible.
- **Reproducibilidad del seed** — el seed original usaba `Faker.seed(42)` y `random.seed(42)` para garantizar que el mismo dataset se generara en cada ejecución. Al reemplazar las llamadas a Faker con f-strings simples, se pierde esa capacidad: el contenido de posts y comments ya no depende de la semilla. Se ignoró deliberadamente porque la reproducibilidad exacta del contenido no es relevante para datos de desarrollo — lo que importa es la distribución (power law de autores, long tail de comments), que sí se preserva vía `random.seed(42)`.

## Qué haría a continuación

- Aplicar el fix de `k=chunk_size` en `posts.py` también.
- Perfilar los endpoints de la API — el README sugiere que algunos son lentos, probablemente N+1 queries en el detalle de post con comments.
- Agregar índices en la DB donde corresponda basándose en análisis de queries con `EXPLAIN ANALYZE`.
- Containerizar con Docker Compose (app + postgres) para mejorar la developer experience — actualmente el setup requiere una instancia local de Postgres con configuración manual.
- Agregar un pipeline de CI que corra los smoke tests en cada push.

## Herramientas utilizadas

- **py-spy** — sampling profiler. Generó flamegraphs en speedscope en cada iteración para identificar cuellos de botella. Fue por lejos la herramienta más útil — cada flamegraph apuntó inmediatamente al siguiente fix sin necesidad de adivinar.
- **Claude Code** — utilizado a lo largo del proceso para pair programming. Transcripción de la conversación disponible bajo pedido.
