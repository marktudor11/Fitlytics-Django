from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    # nutrition is provided by the nutrition app (included in project urls).
    # Keep core.urls focused on small top-level routes.
    path("training/", views.training, name="training"),
    path("metrics/", views.metrics, name="metrics"),
]
