import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from blog.models import Comment

from .posts import PostFactory
from .users import UserFactory


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    body = factory.Faker("sentence", nb_words=15)
    created_at = factory.LazyFunction(timezone.now)
