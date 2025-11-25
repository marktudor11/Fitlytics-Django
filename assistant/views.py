from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.conf import settings
import google.generativeai as gen
import os

MODEL_CANDIDATES = [
    "models/gemini-flash-latest",
    "models/gemini-pro-latest",
]

def _model():
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    if not api_key:
        return None
    # System instruction keeps responses brief and domain-limited
    for name in MODEL_CANDIDATES:
        try:
            return gen.GenerativeModel(name, system_instruction="Answer briefly. Focus on fitness and nutrition. Use provided user stats if helpful.")
        except Exception:
            pass
    return None

# --- new: session chat history helpers + user stats context ---
def _get_history(session):
    return session.get("assistant_chat_history", [])

def _append_history(session, role, text):
    hist = session.get("assistant_chat_history", [])
    hist.append({"role": role, "parts": [text]})
    session["assistant_chat_history"] = hist[-10:]  # keep last 10 turns
    session.modified = True

def _user_stats_text(user):
    # Pull what exists, safely. Adapt to your schema (e.g., Profile, Metrics).
    src = getattr(user, "profile", user)
    fields = []
    for label, attr in [
        ("Weight (kg)", "weight_kg"),
        ("Height (cm)", "height_cm"),
        ("Age", "age"),
        ("Sex", "sex"),
        ("Goal", "goal"),
        ("Weekly Workouts", "weekly_workouts"),
    ]:
        val = getattr(src, attr, None)
        if val not in (None, ""):
            fields.append(f"{label}: {val}")
    return "\n".join(fields)

@csrf_exempt  # for quick start; switch to CSRF token in production
@require_POST
@login_required
def ai_chat(request):
    q = strip_tags(request.POST.get("q", "")).strip()
    if not q:
        return JsonResponse({"ok": False, "answer": "Empty question."}, status=400)
    m = _model()
    if m is None:
        return JsonResponse({"ok": False, "answer": "API key missing or model unavailable."}, status=500)

    try:
        gen.configure(api_key=(settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""))
        history = _get_history(request.session)
        chat = m.start_chat(history=history)

        stats = _user_stats_text(request.user)
        prompt = q if not stats else f"User stats:\n{stats}\n\nQuestion: {q}"

        resp = chat.send_message(prompt)
        answer = (getattr(resp, "text", "") or "").strip()

        # persist this turn
        _append_history(request.session, "user", q)
        _append_history(request.session, "model", answer or "No answer.")

        return JsonResponse({"ok": True, "answer": answer or "No answer."})
    except Exception as e:
        return JsonResponse({"ok": False, "answer": f"Error: {e}"}, status=500)