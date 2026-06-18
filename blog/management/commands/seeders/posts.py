import random
from datetime import timedelta

from django.db import transaction

from blog.models import Post

from .utils import random_time

TITLE_POOL_SIZE = 10_000
BODY_POOL_SIZE = 10_000


def seed_posts(fake, user_ids, author_weights, now, three_years_ago, num_posts, batch):
    recency_cutoff = now - timedelta(days=180)
    title_pool = [f"Post title {i}" for i in range(TITLE_POOL_SIZE)]
    body_pool = [f"Post body {i}" for i in range(BODY_POOL_SIZE)]

    with transaction.atomic():
        for chunk_start in range(0, num_posts, batch):
            chunk = []
            for i in range(chunk_start, min(chunk_start + batch, num_posts)):
                if random.random() < 0.5:
                    ts = random_time(recency_cutoff, now)
                else:
                    ts = random_time(three_years_ago, now)
                author_id = random.choices(user_ids, weights=author_weights, k=1)[0]
                chunk.append(
                    Post(
                        author_id=author_id,
                        title=random.choice(title_pool),
                        body=random.choice(body_pool),
                        is_published=random.random() < 0.9,
                        view_count=random.randint(0, 5000),
                        created_at=ts,
                    )
                )
            Post.objects.bulk_create(chunk, batch_size=batch)

    return list(Post.objects.values_list("id", flat=True))


def attach_post_tags(post_ids, hot_tag_ids, cold_tag_ids, tags_per_post_avg, batch):
    through = Post.tags.through
    m2m_rows = []
    for pid in post_ids:
        n_tags = max(1, int(random.gauss(tags_per_post_avg, 1)))
        chosen = set()
        for _ in range(n_tags):
            if random.random() < 0.4 and hot_tag_ids:
                chosen.add(random.choice(hot_tag_ids))
            else:
                chosen.add(random.choice(cold_tag_ids))
        for tid in chosen:
            m2m_rows.append(through(post_id=pid, tag_id=tid))
        if len(m2m_rows) >= batch * 10:
            with transaction.atomic():
                through.objects.bulk_create(m2m_rows, batch_size=batch, ignore_conflicts=True)
            m2m_rows = []
    if m2m_rows:
        with transaction.atomic():
            through.objects.bulk_create(m2m_rows, batch_size=batch, ignore_conflicts=True)
