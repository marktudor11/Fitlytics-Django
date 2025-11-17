from django.urls import path
from . import views

app_name = "assistant"

urlpatterns = [
    path("chat/", views.ai_chat, name="chat"),
]