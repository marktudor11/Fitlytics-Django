from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
import logging

from .models import Meal
from .forms import MealForm

logger = logging.getLogger(__name__)


def nutrition_home(request):
    """Show nutrition dashboard. Anonymous users can view summaries but must log in to add meals.

    POST: only allowed for authenticated users; anonymous POSTs are redirected to login with next.
    GET: if authenticated, include a MealForm in context; otherwise show a login prompt.
    """
    today = timezone.localdate()

    form = None
    if request.method == "POST":
        # require login to create meals
        if not request.user.is_authenticated:
            login_url = f"{reverse('accounts:login')}?next={request.path}"
            return redirect(login_url)

        logger.debug("Nutrition POST payload: %s", request.POST)
        form = MealForm(request.POST)
        if form.is_valid():
            try:
                meal = form.save(commit=False)
                meal.user = request.user
                meal.save()
                messages.success(request, "Meal added.")
                return redirect("nutrition:home")
            except Exception:
                logger.exception("Failed to save Meal for user %s", request.user)
                messages.error(request, "Failed to save meal. Check server logs.")
        else:
            logger.warning("Meal form invalid: %s", form.errors.as_json())
            messages.error(request, "Please fix the errors below.")
    else:
        if request.user.is_authenticated:
            form = MealForm()

    # meals for today (only query for authenticated users)
    if request.user.is_authenticated:
        meals = Meal.objects.filter(user=request.user, created_at__date=today).order_by("-created_at")
    else:
        meals = Meal.objects.none()

    totals = meals.aggregate(
        calories=Sum("calories"),
        protein=Sum("protein"),
        carbs=Sum("carbs"),
        fat=Sum("fat"),
    )

    # ensure numeric zeros instead of None
    totals = {k: (v or 0) for k, v in totals.items()}

    ctx = {"today": today, "form": form, "meals": meals, "totals": totals}
    return render(request, "nutrition.html", ctx)