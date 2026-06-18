from django.db import transaction

from blog.models import User

from .utils import random_time


def seed_users(fake, now, three_years_ago, num_users, batch):
    users = [
        User(
            username=f"user{i:05d}",
            email=f"user{i:05d}@example.com",
            display_name=fake.name(),
            bio=fake.text(max_nb_chars=200) if i % 4 == 0 else "",
            created_at=random_time(three_years_ago, now),
        )
        for i in range(num_users)
    ]
    with transaction.atomic():
        User.objects.bulk_create(users, batch_size=batch)
    return list(User.objects.values_list("id", flat=True))
