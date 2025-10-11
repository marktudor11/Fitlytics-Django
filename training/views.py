from django.shortcuts import render
from django.utils import timezone

def training_home(request):
    today = timezone.localdate()

    # Placeholder totals (replace with real aggregates later)
    totals = {
        "volume": 0,
        "sets": 0,
        "exercises": 0,
        "duration_min": 0,
    }

    # Example structure the template expects; safe to leave empty for now
    workouts = [
        # {
        #     "date": today,
        #     "duration_min": 60,
        #     "notes": "Push day — tempo bench",
        #     "volume": 8200,
        #     "exercises": [
        #         {
        #             "name": "Barbell Bench Press",
        #             "muscle_group": "Chest",
        #             "is_compound": True,
        #             "sets": [
        #                 {"reps": 8, "weight_kg": 60, "rir": 2, "is_warmup": False},
        #                 {"reps": 8, "weight_kg": 60, "rir": 2, "is_warmup": False},
        #             ],
        #         }
        #     ],
        # },
    ]

    recent_prs = []     # e.g., [{"exercise_name": "Deadlift", "pr_weight_kg": 180, "pr_reps": 1, "achieved_at": today}]
    top_volume = []     # e.g., [{"exercise_name": "Squat", "volume": 24000}]

    ctx = {
        "today": today,
        "totals": totals,
        "workouts": workouts,
        "recent_prs": recent_prs,
        "top_volume": top_volume,
    }
    return render(request, "training.html", ctx)
