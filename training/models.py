from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone


class TrainingSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="training_sessions"
    )
    name = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.localdate)
    duration_min = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        label = self.name or "Workout"
        return f"{label} — {self.date}"

    def exercises_count(self):
        return self.exercises.count()

    def sets_count(self):
        return sum(ex.sets.count() for ex in self.exercises.all())

    def total_volume(self):
        # kg·reps: sum(reps * weight_kg) across all sets (skip sets without weight)
        total = 0
        for ex in self.exercises.all():
            for s in ex.sets.all():
                if s.weight_kg:
                    total += float(s.weight_kg) * s.reps
        return total or 0

    def total_duration(self):
        return self.duration_min or 0


class Exercise(models.Model):
    MUSCLE_CHOICES = (
        ("", "Unspecified"),
        ("Chest", "Chest"),
        ("Back", "Back"),
        ("Legs", "Legs"),
        ("Shoulders", "Shoulders"),
        ("Arms", "Arms"),
        ("Core", "Core"),
        ("Full Body", "Full Body"),
    )

    session = models.ForeignKey(
        TrainingSession, on_delete=models.CASCADE, related_name="exercises"
    )
    name = models.CharField(max_length=255)
    muscle_group = models.CharField(max_length=50, choices=MUSCLE_CHOICES, blank=True)
    is_compound = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name

    def volume(self):
        total = 0
        for s in self.sets.all():
            if s.weight_kg:
                total += float(s.weight_kg) * s.reps
        return total or 0


class Set(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="sets")
    order = models.PositiveIntegerField(default=0)
    reps = models.PositiveIntegerField()
    weight_kg = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    rir = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    is_warmup = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        w = f"{self.weight_kg}kg" if self.weight_kg is not None else "bw"
        return f"{self.reps} x {w}"

    def volume(self):
        return (float(self.weight_kg) * self.reps) if self.weight_kg else 0