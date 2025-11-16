from django.http import JsonResponse
from django.views.decorators.http import require_POST, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.conf import settings
import google.generativeai as gen

def _model():
    if not settings.GEMINI_API_KEY:
        return None
    gen.configure(api_key=settings.GEMINI_API_KEY)
    return gen.GenerativeModel("gemini-1.5-flash")

@csrf_exempt
@require_POST
@login_required
def ai_chat(request):
    q = strip_tags(request.POST.get("q", "")).strip()
    if not q:
        return JsonResponse({"ok": False, "answer": "Empty question."}, status=400)
    m = _model()
    if m is None:
        return JsonResponse({"ok": False, "answer": "API key missing."}, status=500)
    try:
        resp = m.generate_content(
            "Answer briefly (bullets ok). Fitness & nutrition only.\nUser: " + q
        )
        return JsonResponse({"ok": True, "answer": (resp.text or "").strip()})
    except Exception as e:
        return JsonResponse({"ok": False, "answer": f"Error: {e}"}, status=500)