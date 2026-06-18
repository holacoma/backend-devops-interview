import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from blog.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n:05d}")
    email = factory.Sequence(lambda n: f"user{n:05d}@example.com")
    display_name = factory.Faker("name")
    bio = factory.Maybe(
        factory.Faker("boolean", chance_of_getting_true=25),
        yes_declaration=factory.Faker("text", max_nb_chars=200),
        no_declaration="",
    )
    created_at = factory.LazyFunction(timezone.now)
