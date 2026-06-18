import random

from django.db import transaction

from blog.models import Comment

from .utils import long_tail_weights, random_time


def seed_comments(fake, post_ids, user_ids, author_weights, now, three_years_ago, num_comments, batch):
    post_weights = long_tail_weights(len(post_ids), top_pct=0.01, top_share=0.5)
    for chunk_start in range(0, num_comments, batch):
        chunk = []
        for _ in range(chunk_start, min(chunk_start + batch, num_comments)):
            pid = random.choices(post_ids, weights=post_weights, k=1)[0]
            aid = random.choices(user_ids, weights=author_weights, k=1)[0]
            chunk.append(
                Comment(
                    post_id=pid,
                    author_id=aid,
                    body=fake.sentence(nb_words=random.randint(5, 30)),
                    created_at=random_time(three_years_ago, now),
                )
            )
        Comment.objects.bulk_create(chunk, batch_size=batch)
