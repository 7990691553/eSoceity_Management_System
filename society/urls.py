from django.contrib import admin
from django.urls import path
from . import views

app_name = "society"

urlpatterns = [
    path("", views.dashboard_redirect, name="dashboard_redirect"),

    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("security/", views.security_dashboard, name="security_dashboard"),
    path("member/", views.member_dashboard, name="member_dashboard"),
    path("helper/", views.helper_dashboard, name="helper_dashboard"),

    path("visitors/", views.visitor_list, name="visitor_list"),
    path("visitors/add/", views.add_visitor, name="add_visitor"),

    path("deliveries/", views.delivery_list, name="delivery_list"),
    path("deliveries/add/", views.add_delivery, name="add_delivery"),

    path("children/", views.child_list, name="child_list"),
    path("children/add/", views.add_child, name="add_child"),

    path("staff/", views.staff_list, name="staff_list"),
    path("staff/add/", views.add_staff, name="add_staff"),

    path("notices/", views.notice_list, name="notice_list"),
    path("notices/add/", views.add_notice, name="add_notice"),
]