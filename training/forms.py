from django import forms
from django.forms.models import inlineformset_factory
from .models import TrainingSession, Exercise, Set


class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ["name", "date", "duration_min", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "input"}, format="%Y-%m-%d"),
            "name": forms.TextInput(attrs={"class": "input", "placeholder": "Session name (optional)"}),
            "duration_min": forms.NumberInput(attrs={"class": "input", "min": 0}),
            "notes": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "muscle_group", "is_compound", "order", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": "Exercise name"}),
            "muscle_group": forms.Select(attrs={"class": "input"}),
            "is_compound": forms.CheckboxInput(attrs={"class": "checkbox"}),
            "order": forms.NumberInput(attrs={"class": "input", "min": 0}),
            "notes": forms.Textarea(attrs={"class": "input", "rows": 2}),
        }


class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        fields = ["order", "reps", "weight_kg", "rir", "is_warmup"]
        widgets = {
            "order": forms.NumberInput(attrs={"class": "input", "min": 0}),
            "reps": forms.NumberInput(attrs={"class": "input", "min": 1}),
            "weight_kg": forms.NumberInput(attrs={"class": "input", "step": "0.25", "min": 0}),
            "rir": forms.NumberInput(attrs={"class": "input", "step": "0.5", "min": 0}),
            "is_warmup": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }

    def clean_reps(self):
        reps = self.cleaned_data.get("reps")
        if reps is None or reps <= 0:
            raise forms.ValidationError("Reps must be a positive integer.")
        return reps


# Inline formsets to be used in views for nested editing
ExerciseFormSet = inlineformset_factory(
    TrainingSession,
    Exercise,
    form=ExerciseForm,
    extra=1,
    can_delete=True,
    min_num=0,
)

SetFormSet = inlineformset_factory(
    Exercise,
    Set,
    form=SetForm,
    extra=1,
    can_delete=True,
    min_num=0,