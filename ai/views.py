from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from society.views import role_required

from .services.insights import generate_ai_insight
from .services.alerts import generate_smart_alerts
from .services.risk_analysis import generate_risk_watchlist
from .services.health_score import generate_society_health_score
from .services.copilot import generate_copilot_context


@login_required
@role_required("super_admin", "chairman")
def ai_dashboard(request):
    insight = generate_ai_insight()
    alerts = generate_smart_alerts()
    watchlist = generate_risk_watchlist()
    health = generate_society_health_score(alert_count=len(alerts))

    context = {
        "insight": insight,
        "alerts": alerts,
        "alert_count": len(alerts),
        "watchlist": watchlist,
        "watchlist_count": len(watchlist),
        "health": health,
    }
    return render(request, "ai/dashboard.html", context)


@login_required
@role_required("super_admin", "chairman", "security", "member", "helper")
def copilot_dashboard(request):
    copilot = generate_copilot_context(request.user)
    return render(request, "ai/copilot.html", {"copilot": copilot})