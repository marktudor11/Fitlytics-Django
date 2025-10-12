from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    GENDER = (("Male", "Male"), ("Female", "Female"), ("Other", "Other"))
    GOAL = (("Lose Weight", "Lose Weight"),
            ("Maintain Weight", "Maintain Weight"),
            ("Gain Muscle", "Gain Muscle"))
    ACTIVITY = (
        ("Sedentary (little exercise)", "Sedentary (little exercise)"),
        ("Lightly Active (1-3 days/week)", "Lightly Active (1-3 days/week)"),
        ("Active (3-5 days/week)", "Active (3-5 days/week)"),
        ("Very Active (6-7 days/week)", "Very Active (6-7 days/week)"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=12, choices=GENDER)
    height_cm = models.FloatField()
    weight_kg = models.FloatField()
    goal = models.CharField(max_length=20, choices=GOAL)
    activity_level = models.CharField(max_length=40, choices=ACTIVITY)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.user.username} Profile"
