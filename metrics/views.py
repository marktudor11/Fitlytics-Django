from datetime import timedelta, datetime, time
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count, Value, DecimalField, DateTimeField, FloatField, IntegerField, ExpressionWrapper
from django.db.models.functions import Cast
from django.db.models.functions import TruncDate, Coalesce
from django.shortcuts import render
from django.utils import timezone
import logging

from nutrition.models import Meal
from training.models import Set, TrainingSession

logger = logging.getLogger(__name__)


def _last_n_days(days=30):
    end = timezone.localdate()
    start = end - timedelta(days=days - 1)
    labels = [start + timedelta(days=i) for i in range(days)]
    return start, end, [d.isoformat() for d in labels]


def _meal_date_field():
    """
    Detect which date-like field the Meal model has.
    Prefer 'date' if present, else 'created_at', else 'created_on', else 'consumed_at'.
    Returns (field_name, is_datetime)
    """
    candidates = ("date", "created_at", "created_on", "consumed_at")
    for name in candidates:
        try:
            fld = Meal._meta.get_field(name)
            return name, isinstance(fld, DateTimeField)
        except Exception:
            continue
    # fallback: assume created_at DateTime
    return "created_at", True


@login_required
def metrics_home(request):
    start, end, labels = _last_n_days(30)

    # ---------- Nutrition: per-day sums (timezone-aware local day) ----------
    meal_date_field, is_dt = _meal_date_field()
    tz = timezone.get_current_timezone()
    if is_dt:
        # Group by local-day using TruncDate; no date-range filter to avoid tz edge-cases
        filt = {
            "user": request.user,
        }
        day_expr = TruncDate(meal_date_field, tzinfo=tz)
    else:
        # DateField: still use TruncDate for consistency
        filt = {
            "user": request.user,
        }
        day_expr = TruncDate(meal_date_field)

    nut = (
        Meal.objects.filter(**filt)
        .annotate(day=day_expr)
        .values("day")
        .annotate(
            calories=Coalesce(Sum("calories"), Value(0), output_field=IntegerField()),
            protein=Coalesce(Sum("protein"), Value(0.0), output_field=FloatField()),
            carbs=Coalesce(Sum("carbs"), Value(0.0), output_field=FloatField()),
            fat=Coalesce(Sum("fat"), Value(0.0), output_field=FloatField()),
        )
    )
    nut_map = {row["day"].isoformat(): row for row in nut}
    calories = [int(nut_map.get(d, {}).get("calories", 0) or 0) for d in labels]
    protein = [float(nut_map.get(d, {}).get("protein", 0) or 0) for d in labels]
    carbs = [float(nut_map.get(d, {}).get("carbs", 0) or 0) for d in labels]
    fat = [float(nut_map.get(d, {}).get("fat", 0) or 0) for d in labels]
    try:
        logger.warning(
            "Metrics nutrition: rows=%s total_cal=%s", len(nut_map), sum(calories)
        )
    except Exception:
        logger.warning("Metrics nutrition logging failed")

    # ---------- Training: per-day totals from sets ----------
    # Assume TrainingSession has a DateField named 'date'
    # Build volume safely as Decimal: weight_kg (Decimal) * reps (cast to Decimal)
    vol_field = DecimalField(max_digits=14, decimal_places=2)
    train_qs = (
        Set.objects.filter(
            exercise__session__user=request.user,
        )
        .annotate(day=F("exercise__session__date"))
        .annotate(
            vol_raw=ExpressionWrapper(
                F("weight_kg") * Cast(F("reps"), output_field=vol_field),
                output_field=vol_field,
            )
        )
        .annotate(
            volume=Coalesce(
                F("vol_raw"),
                Value(0, output_field=vol_field),
                output_field=vol_field,
            )
        )
        .values("day")
        .annotate(
            total_volume=Coalesce(
                Sum("volume"), Value(0, output_field=vol_field), output_field=vol_field
            ),
            total_sets=Coalesce(Count("id"), 0),
        )
    )
    train_map = {row["day"].isoformat(): row for row in train_qs}
    train_volume = [float(train_map.get(d, {}).get("total_volume", 0) or 0) for d in labels]
    train_sets = [int(train_map.get(d, {}).get("total_sets", 0) or 0) for d in labels]
    try:
        logger.warning(
            "Metrics training: rows=%s total_volume=%s total_sets=%s",
            len(train_map), sum(train_volume), sum(train_sets)
        )
    except Exception:
        logger.warning("Metrics training logging failed")

   
    today = timezone.localdate()
    today_key = today.isoformat()
    if today_key in labels:
        idx = labels.index(today_key)
        # Nutrition fallback
        if calories[idx] == 0 and protein[idx] == 0 and carbs[idx] == 0 and fat[idx] == 0:
            agg = (
                Meal.objects.filter(user=request.user, created_at__date=today)
                .aggregate(
                    calories=Coalesce(Sum("calories"), Value(0), output_field=IntegerField()),
                    protein=Coalesce(Sum("protein"), Value(0.0), output_field=FloatField()),
                    carbs=Coalesce(Sum("carbs"), Value(0.0), output_field=FloatField()),
                    fat=Coalesce(Sum("fat"), Value(0.0), output_field=FloatField()),
                )
            )
            calories[idx] = int(agg.get("calories") or 0)
            protein[idx] = float(agg.get("protein") or 0)
            carbs[idx] = float(agg.get("carbs") or 0)
            fat[idx] = float(agg.get("fat") or 0)
        # Training fallback
        if train_volume[idx] == 0 and train_sets[idx] == 0:
            t_agg = (
                Set.objects.filter(exercise__session__user=request.user, exercise__session__date=today)
                .annotate(vol=Coalesce(F("weight_kg") * F("reps"), Value(0), output_field=DecimalField(max_digits=14, decimal_places=2)))
                .aggregate(total_volume=Coalesce(Sum("vol"), Value(0), output_field=DecimalField(max_digits=14, decimal_places=2)), total_sets=Coalesce(Count("id"), 0))
            )
            try:
                train_volume[idx] = float(t_agg.get("total_volume") or 0)
            except Exception:
                train_volume[idx] = 0.0
            train_sets[idx] = int(t_agg.get("total_sets") or 0)

    ctx = {
        "labels": labels,
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "train_volume": train_volume,
        "train_sets": train_sets,
        # debug counts for page 
        "nut_count": len(nut_map),
        "train_count": len(train_map),
        "cal_sum": sum(calories) if calories else 0,
        "train_set_sum": sum(train_sets) if train_sets else 0,
        "train_vol_sum": float(sum(train_volume)) if train_volume else 0.0,
    }
    return render(request, "metrics.html", ctx)