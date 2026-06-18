from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

from blog.api import router as blog_router

api = NinjaAPI()
api.add_router("/", blog_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("silk/", include("silk.urls", namespace="silk")),
]
