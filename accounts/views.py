from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse
import logging
import traceback
from django.db import transaction

from .forms import SignupForm, LoginForm

User = get_user_model()

logger = logging.getLogger(__name__)


def login_view(request):
    """
    Accepts either email or username in the 'email' field (keeps your current UI).
    Uses LoginForm for server-side validation.
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get("user")
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect("core:home")
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return render(request, "login.html", {"form": form}, status=401)

    form = LoginForm()
    return render(request, "login.html", {"form": form})


def signup_view(request):
    """
    Uses SignupForm.create_user_and_profile() to atomically create the User and Profile.
    Logs the user in on success.
    """
    # Ensure form is always defined so template rendering on GET works
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                # Create user & profile inside a DB transaction, then login after commit
                with transaction.atomic():
                    user = form.create_user_and_profile()
                # perform login after the transaction block completes (so session save is outside the transaction)
                try:
                    login(request, user)
                except Exception:
                    logger.exception("Login/session save failed after creating user")
                    traceback.print_exc()
                    messages.error(request, "Account created but automatic login failed; please log in manually.")
                    return redirect("accounts:login")

                messages.success(request, "Account created. Welcome!")
                return redirect("core:home")
            except Exception:
                # Log full exception to console to diagnose DB / integrity issues
                logger.exception("Error creating user/profile during signup")
                traceback.print_exc()
                messages.error(request, "Could not create account. Please try again; the server logged the error.")
        else:
            # surface form errors to console for debugging
            logger.warning("Signup form validation failed: %s", form.errors.as_json())
            messages.error(request, "Please fix the errors below: %s" % form.errors)
        # fallthrough: render signup with posted form and errors
        return render(request, "signup.html", {"form": form}, status=400)

    # GET: empty form
    form = SignupForm()
    return render(request, "signup.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You’ve been logged out.")
    return redirect("core:home")