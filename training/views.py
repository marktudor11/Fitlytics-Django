from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
import logging
from datetime import date
from decimal import Decimal, InvalidOperation

from .models import TrainingSession
from .forms import TrainingSessionForm

logger = logging.getLogger(__name__)


def training_home(request):
    today = timezone.localdate()

    # list sessions for the current user (empty for anonymous)
    if request.user.is_authenticated:
        sessions = (
            TrainingSession.objects.filter(user=request.user)
            .order_by("-date", "-created_at")
            .prefetch_related("exercises__sets")
            .all()
        )
    else:
        sessions = TrainingSession.objects.none()

    # handle create-session POST (only for authenticated users)
    if request.method == "POST":
        if not request.user.is_authenticated:
            # redirect anonymous posters to login, preserving next
            return redirect(f"{reverse('accounts:login')}?next={request.path}")

        # Parse workout-level fields
        workout_date = request.POST.get("workout_date")
        duration_min = request.POST.get("duration_min") or None
        notes = request.POST.get("notes", "")

        exercise_name = request.POST.get("exercise_name")
        muscle_group = request.POST.get("muscle_group", "")
        is_compound = bool(request.POST.get("is_compound"))

        reps_list = request.POST.getlist("reps[]")
        weight_list = request.POST.getlist("weight_kg[]")
        rir_list = request.POST.getlist("rir[]")
        # Because checkboxes don't send unchecked values, we include a hidden input in the template
        # so is_warmup_list will align with other arrays. See template change.
        is_warmup_list = request.POST.getlist("is_warmup[]")

        logger.debug("Training POST payload: date=%s duration=%s exercise=%s reps=%s", workout_date, duration_min, exercise_name, reps_list)

        # Basic validation
        if not exercise_name or not reps_list:
            messages.error(request, "Please provide an exercise name and at least one set.")
            form = TrainingSessionForm() if request.user.is_authenticated else None
        else:
            try:
                # create TrainingSession
                # Coerce date string to a date object if provided
                try:
                    parsed_date = date.fromisoformat(workout_date) if workout_date else timezone.localdate()
                except Exception:
                    parsed_date = timezone.localdate()

                session = TrainingSession.objects.create(
                    user=request.user,
                    name=exercise_name,
                    date=parsed_date,
                    duration_min=(int(duration_min) if duration_min else None),
                    notes=notes,
                )

                # create Exercise
                ex = session.exercises.create(
                    name=exercise_name,
                    muscle_group=muscle_group,
                    is_compound=is_compound,
                    order=0,
                )

                # create Sets
                for idx, reps_raw in enumerate(reps_list):
                    try:
                        reps = int(reps_raw)
                    except Exception:
                        reps = None

                    weight = None
                    if idx < len(weight_list):
                        w = weight_list[idx]
                        try:
                            weight = Decimal(w) if w != "" else None
                        except (InvalidOperation, Exception):
                            weight = None

                    rir = None
                    if idx < len(rir_list):
                        r = rir_list[idx]
                        try:
                            rir = Decimal(r) if r != "" else None
                        except (InvalidOperation, Exception):
                            rir = None

                    is_warmup = False
                    if idx < len(is_warmup_list):
                        # template now sends '0' or '1' for each row; interpret '1' as True
                        is_warmup = (is_warmup_list[idx] == "1")

                    if reps:
                        ex.sets.create(
                            order=idx,
                            reps=reps,
                            weight_kg=weight,
                            rir=rir,
                            is_warmup=is_warmup,
                        )

                messages.success(request, "Training session and sets saved.")
                return redirect("training:home")
            except Exception:
                logger.exception("Failed to save training POST")
                messages.error(request, "Failed to save training. Check server logs.")
            form = TrainingSessionForm() if request.user.is_authenticated else None
    else:
        form = TrainingSessionForm() if request.user.is_authenticated else None

    ctx = {
        "today": today,
        "totals": {
            "volume": sum(s.total_volume() for s in sessions) if request.user.is_authenticated else 0,
            "sets": sum(s.sets_count() for s in sessions) if request.user.is_authenticated else 0,
            "exercises": sum(s.exercises_count() for s in sessions) if request.user.is_authenticated else 0,
            "duration_min": sum((s.duration_min or 0) for s in sessions) if request.user.is_authenticated else 0,
        },
        "workouts": sessions,
        "form": form,
    }
    return render(request, "training/training.html", ctx)