from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "gender", "height_cm", "weight_kg", "goal", "activity_level", "created_at")
    search_fields = ("userusername", "useremail")
    list_filter = ("gender", "goal", "activity_level")