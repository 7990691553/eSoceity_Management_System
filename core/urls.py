from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('signup/',views.UserSignupView,name='signup'),
    path('login/',views.userLoginView,name='login')
]