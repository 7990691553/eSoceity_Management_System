from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from society.views import role_required
from .services.insights import generate_ai_insight
from .models import AIInsight


@login_required
@role_required("super_admin", "chairman")
def ai_dashboard(request):

    insight = AIInsight.objects.first()

    if not insight:
        insight = generate_ai_insight()

    context = {
        "insight": insight
    }

    return render(request, "ai/dashboard.html", context)