from django.db import transaction
from django.utils.text import slugify

from blog.models import Tag


def seed_tags(fake, now, num_tags, batch):
    hot_slugs = ["python", "django", "postgres", "devops", "sre"]
    tag_objs = [Tag(name=s.title(), slug=s, created_at=now) for s in hot_slugs]
    for _ in range(num_tags - len(hot_slugs)):
        word = fake.unique.word()
        tag_objs.append(Tag(name=word.title(), slug=slugify(word), created_at=now))
    with transaction.atomic():
        Tag.objects.bulk_create(tag_objs, batch_size=batch)
    tags = list(Tag.objects.all().only("id", "slug"))
    hot_tag_ids = [t.id for t in tags if t.slug in hot_slugs]
    cold_tag_ids = [t.id for t in tags if t.slug not in hot_slugs]
    return hot_tag_ids, cold_tag_ids
