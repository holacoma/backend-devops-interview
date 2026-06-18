import factory
from django.utils import timezone
from django.utils.text import slugify
from factory.django import DjangoModelFactory

from blog.models import Tag


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    created_at = factory.LazyFunction(timezone.now)
