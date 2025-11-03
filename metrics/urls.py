
from django.urls import path
from . import views

app_name = "metrics"

urlpatterns = [
    path("", views.metrics_home, name="home"),
]