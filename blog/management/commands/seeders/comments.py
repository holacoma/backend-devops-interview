import random

from django.db import transaction

from blog.models import Comment

from .utils import long_tail_weights, random_time


def seed_comments(fake, post_ids, user_ids, author_weights, now, three_years_ago, num_comments, batch):
    post_weights = long_tail_weights(len(post_ids), top_pct=0.01, top_share=0.5)
    for chunk_start in range(0, num_comments, batch):
        chunk_size = min(batch, num_comments - chunk_start)
        chunk_post_ids = random.choices(post_ids, weights=post_weights, k=chunk_size)
        chunk_author_ids = random.choices(user_ids, weights=author_weights, k=chunk_size)
        chunk = [
            Comment(
                post_id=chunk_post_ids[i],
                author_id=chunk_author_ids[i],
                body=f"Comment body {chunk_start + i}",
                created_at=random_time(three_years_ago, now),
            )
            for i in range(chunk_size)
        ]
        with transaction.atomic():
            Comment.objects.bulk_create(chunk, batch_size=batch)
