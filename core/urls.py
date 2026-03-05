from django.contrib import admin
from django.urls import include, path
from . import views

app_name = "core"

urlpatterns = [
    path('signup/',views.UserSignupView,name='signup'),
    path('login/',views.userLoginView,name='login')
]