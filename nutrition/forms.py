from django import forms
from .models import Meal


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ["meal_type", "food_name", "calories", "protein", "carbs", "fat"]
        widgets = {
            "meal_type": forms.Select(attrs={"class": "meal-select"}),
            "food_name": forms.TextInput(attrs={"placeholder": "Grilled Chicken"}),
            "calories": forms.NumberInput(attrs={"placeholder": "300"}),
            "protein": forms.NumberInput(attrs={"placeholder": "30"}),
            "carbs": forms.NumberInput(attrs={"placeholder": "20"}),
            "fat": forms.NumberInput(attrs={"placeholder": "10"}),
        }
