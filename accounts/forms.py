from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Profile


class SignupForm(forms.Form):
    # Matches your signup.html input names exactly
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    age = forms.IntegerField(min_value=13, max_value=100)
    gender = forms.ChoiceField(choices=Profile.GENDER)
    height_cm = forms.FloatField(min_value=50, max_value=300)
    weight_kg = forms.FloatField(min_value=20, max_value=400)
    goal = forms.ChoiceField(choices=Profile.GOAL)
    activity_level = forms.ChoiceField(choices=Profile.ACTIVITY)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def create_user_and_profile(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
        )
        Profile.objects.create(
            user=user,
            age=data["age"],
            gender=data["gender"],
            height_cm=data["height_cm"],
            weight_kg=data["weight_kg"],
            goal=data["goal"],
            activity_level=data["activity_level"],
        )
        return user


class LoginForm(forms.Form):
   
    email = forms.CharField()          # can be email or username
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned = super().clean()
        ident = cleaned.get("email", "").strip()
        password = cleaned.get("password", "")

        # Try to resolve a username from an email; fall back to ident as username
        try:
            user = User.objects.get(email__iexact=ident)
            username = user.username
        except User.DoesNotExist:
            username = ident

        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid email/username or password.")
        cleaned["user"] = user
        return cleaned
