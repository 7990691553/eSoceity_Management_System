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

    path("search/", views.search_page, name="search_page"),
    path("search/suggest/", views.search_suggest, name="search_suggest"),

    path("visitor-logs/", views.visitor_log_list, name="visitor_log_list"),
    path("visitor-logs/add/", views.add_visitor_log, name="add_visitor_log"),
    path("visitor-logs/<int:pk>/edit/", views.edit_visitor_log, name="edit_visitor_log"),

    path("visitors/<int:id>/approve/", views.approve_visitor, name="approve_visitor"),
    path("visitors/<int:id>/reject/", views.reject_visitor, name="reject_visitor"),

    path("child-logs/", views.child_log_list, name="child_log_list"),
    path("child-logs/add/", views.add_child_log, name="add_child_log"),
    path("child-logs/<int:pk>/edit/", views.edit_child_log, name="edit_child_log"),

    path("delivery-logs/", views.delivery_log_list, name="delivery_log_list"),
    path("delivery-logs/add/", views.add_delivery_log, name="add_delivery_log"),
    path("delivery-logs/<int:pk>/edit/", views.edit_delivery_log, name="edit_delivery_log"),

    path("complaints/", views.complaint_list,   name="complaint_list"),
    path("complaints/add/", views.add_complaint,    name="add_complaint"),
    path("complaints/<int:pk>/", views.complaint_detail, name="complaint_detail"),
    path("complaints/<int:pk>/update/", views.update_complaint, name="update_complaint"),
    path("complaints/<int:pk>/delete/", views.delete_complaint, name="delete_complaint"),
]