from django.urls import path
from . import views

app_name = "ai"

urlpatterns = [
    path("dashboard/", views.ai_dashboard, name="dashboard"),
     path("copilot/", views.copilot_dashboard, name="copilot"),
]