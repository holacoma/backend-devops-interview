# Performance — Notas

## Herramienta de medición

Se agregó [django-silk](https://github.com/jazzband/django-silk) como dependencia de dev. Intercepta cada request, registra las queries SQL ejecutadas (conteo, tiempo, plan) y las expone en `/silk/`. Permite identificar N+1 sin necesidad de leer el código ni instrumentar manualmente.

## Problemas encontrados y resueltos

### N+1 queries — patrón repetido en cuatro endpoints

El modelo tiene dos relaciones que generaban lazy loads: `Post.author` (FK) y `Post.tags` (M2M). `_serialize_post_list` accedía a ambas sin prefetch, disparando un query por post por cada relación. El mismo patrón se repitió en todos los endpoints que devuelven listas de posts.

Solución aplicada de forma consistente:

```python
Post.objects.filter(...)
    .select_related("author")   # JOIN en la query principal, no query extra
    .prefetch_related("tags")   # 1 query batch para toda la M2M
```

En `get_post`, el N+1 era sobre los autores de cada comment. Se resolvió con una query explícita en lugar del patrón `Prefetch(queryset=...)`, que tiene el mismo costo pero es más legible para un objeto único:

```python
Comment.objects.filter(post=post).select_related("author").order_by("created_at")
```

### Sin paginación en `list_posts`

El endpoint retornaba todos los posts de la tabla. Con el dataset completo (~100k posts) daba timeout. Se agregó paginación por página con `page` y `page_size` (default 20, máximo 1000), sin cambiar el contrato de respuesta (`list[PostListOut]`).

## Resultados

Todos los números medidos con django-silk sobre el 1% del dataset (~1k posts, ~5k comments).

| Endpoint | Queries antes | Queries después | Tiempo antes | Tiempo después |
|---|---|---|---|---|
| `GET /api/posts` | 1821 | 2 | 1919ms | 47ms |
| `GET /api/posts/by-tag/{slug}` | 1534 | 3 | 4280ms | 110ms |
| `GET /api/posts/{id}` | 217 | 4 | 351ms | 24ms |
| `GET /api/posts/search` | 1821 | 2 | 1851ms | 127ms |

Los cuatro endpoints daban timeout con el dataset completo. Después del fix responden en decenas de milisegundos.

## Lo que se dejó deliberadamente fuera

**Índice GIN para búsqueda full-text**

`search_posts` usa `icontains` que traduce a `LIKE '%q%'` — seq scan sobre `title` y `body`. Con 1k posts el cuello de botella era el N+1, no el scan. Con el dataset completo sería el siguiente problema: un índice GIN con `pg_trgm` o cambiar a `SearchVector`/`SearchQuery` de `django.contrib.postgres.search` reduciría el tiempo de la query de búsqueda de forma significativa.

**N+1 en `_user_detail`**

`get_user` y `find_user_by_email` hacen dos `COUNT` separados (`user.posts.count()`, `user.comments.count()`). Se puede resolver con `annotate(post_count=Count("posts"), comment_count=Count("comments"))`. No se atacó porque el endpoint no aparecía en los más lentos con el dataset disponible.

**`django-auto-prefetch`**

Librería que resuelve N+1 automáticamente sobreescribiendo el manager — sin necesidad de declarar `select_related`/`prefetch_related` explícitamente. Útil para ir rápido en proyectos grandes. Se descartó porque en este caso los N+1 son puntuales y el approach explícito es más legible y demostrable.
