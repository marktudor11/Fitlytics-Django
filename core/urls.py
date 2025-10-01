from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("nutrition/", views.nutrition, name="nutrition"),
    path("training/", views.training, name="training"),
    path("metrics/", views.metrics, name="metrics"),
]
