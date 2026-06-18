import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from blog.models import Post

from .users import UserFactory


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=8)
    body = factory.Faker("text", max_nb_chars=600)
    is_published = factory.Faker("boolean", chance_of_getting_true=90)
    view_count = factory.Faker("random_int", min=0, max=5000)
    created_at = factory.LazyFunction(timezone.now)
