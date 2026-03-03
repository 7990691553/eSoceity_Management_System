from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .decorators import role_required
from .models import (
    Visitor, Delivery, Child, StaffAttendance, SocietyNotice, SocietySettings
)
from .forms import (
    VisitorForm, DeliveryForm, ChildForm, StaffAttendanceForm, NoticeForm
)


# ---------------- Helpers ----------------

def get_settings():
    """
    Singleton safe fetch/create (pk=1 enforced in model)
    """
    obj, _ = SocietySettings.objects.get_or_create(pk=1)
    return obj


def role_home_url(user):
    """
    Where each role lands after login.
    These are URL names in society/urls.py (app_name='society')
    """
    if user.is_superuser:
        return "society:admin_dashboard"

    role_map = {
        "super_admin": "society:admin_dashboard",
        "chairman": "society:admin_dashboard",
        "security": "society:security_dashboard",
        "member": "society:member_dashboard",
        "helper": "society:helper_dashboard",
    }
    return role_map.get(getattr(user, "role", None), "society:member_dashboard")


# ---------------- Dashboards ----------------

@login_required
def dashboard_redirect(request):
    """
    Single entry route: /society/
    Redirects to role dashboard.
    """
    return redirect(role_home_url(request.user))


@login_required
@role_required("super_admin", "chairman")
def admin_dashboard(request):
    today = now().date()
    context = {
        "settings": get_settings(),
        "visitor_count": Visitor.objects.count(),
        "delivery_count": Delivery.objects.count(),
        "child_count": Child.objects.count(),
        "staff_today": StaffAttendance.objects.filter(attendanceDate=today).count(),
        "recent_visitors": Visitor.objects.order_by("-createdAt")[:5],
        "recent_deliveries": Delivery.objects.order_by("-createdAt")[:5],
        "recent_notices": SocietyNotice.objects.order_by("-createdAt")[:5],
    }
    return render(request, "society/dashboard_admin.html", context)


@login_required
@role_required("security")
def security_dashboard(request):
    today = now().date()
    context = {
        "settings": get_settings(),
        "visitor_pending": Visitor.objects.filter(approvalStatus="PENDING").count(),
        "deliveries_pending": Delivery.objects.filter(deliveryStatus="PENDING").count(),
        "staff_today": StaffAttendance.objects.filter(attendanceDate=today).count(),
        "recent_visitors": Visitor.objects.order_by("-createdAt")[:5],
        "recent_deliveries": Delivery.objects.order_by("-createdAt")[:5],
    }
    return render(request, "society/dashboard_security.html", context)


@login_required
@role_required("member")
def member_dashboard(request):
    user = request.user
    context = {
        "settings": get_settings(),
        "my_visitors": Visitor.objects.filter(memberId=user).order_by("-createdAt")[:6],
        "my_deliveries": Delivery.objects.filter(memberId=user).order_by("-createdAt")[:6],
        "my_children": Child.objects.filter(parentId=user).order_by("childName")[:6],
        "notices": SocietyNotice.objects.order_by("-createdAt")[:5],
    }
    return render(request, "society/dashboard_member.html", context)


@login_required
@role_required("helper")
def helper_dashboard(request):
    context = {
        "notices": SocietyNotice.objects.order_by("-createdAt")[:10]
    }
    return render(request, "society/dashboard_helper.html", context)


# ---------------- VISITOR ----------------

@login_required
def visitor_list(request):
    user = request.user

    if user.is_superuser or getattr(user, "role", None) in ("chairman", "super_admin", "security"):
        visitors = Visitor.objects.all().order_by("-createdAt")
    else:
        visitors = Visitor.objects.filter(memberId=user).order_by("-createdAt")

    return render(request, "society/visitor_list.html", {"visitors": visitors})


@login_required
@role_required("security", "chairman", "super_admin")
def add_visitor(request):
    settings_obj = get_settings()
    if not settings_obj.visitorAllowed:
        messages.error(request, "Visitor entries are currently disabled by society settings.")
        return redirect(role_home_url(request.user))

    form = VisitorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.requestedBy = request.user
        obj.save()
        messages.success(request, "Visitor request created.")
        return redirect("society:visitor_list")

    return render(request, "society/visitor_form.html", {"form": form})


# ---------------- DELIVERY ----------------

@login_required
def delivery_list(request):
    user = request.user

    if user.is_superuser or getattr(user, "role", None) in ("chairman", "super_admin", "security"):
        deliveries = Delivery.objects.all().order_by("-createdAt")
    else:
        deliveries = Delivery.objects.filter(memberId=user).order_by("-createdAt")

    return render(request, "society/delivery_list.html", {"deliveries": deliveries})


@login_required
@role_required("security", "chairman", "super_admin")
def add_delivery(request):
    settings_obj = get_settings()
    if not settings_obj.deliveryAllowed:
        messages.error(request, "Deliveries are currently disabled by society settings.")
        return redirect(role_home_url(request.user))

    form = DeliveryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.receivedBy = request.user
        obj.storedAtSecurity = True
        obj.save()
        messages.success(request, "Delivery recorded.")
        return redirect("society:delivery_list")

    return render(request, "society/delivery_form.html", {"form": form})


# ---------------- CHILD ----------------

@login_required
def child_list(request):
    user = request.user

    if user.is_superuser or getattr(user, "role", None) in ("chairman", "super_admin", "security"):
        children = Child.objects.all().order_by("childName")
    else:
        children = Child.objects.filter(parentId=user).order_by("childName")

    return render(request, "society/child_list.html", {"children": children})


@login_required
@role_required("member", "chairman", "super_admin")
def add_child(request):
    form = ChildForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)

        # members can only add their own child
        if getattr(request.user, "role", None) == "member":
            obj.parentId = request.user

        obj.save()
        messages.success(request, "Child profile added.")
        return redirect("society:child_list")

    return render(request, "society/child_form.html", {"form": form})


# ---------------- STAFF ----------------

@login_required
def staff_list(request):
    staff = StaffAttendance.objects.all().order_by("-attendanceDate")
    return render(request, "society/staff_list.html", {"staff": staff})


@login_required
@role_required("security", "chairman", "super_admin")
def add_staff(request):
    form = StaffAttendanceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.markedBy = request.user
        obj.save()
        messages.success(request, "Staff attendance marked.")
        return redirect("society:staff_list")

    return render(request, "society/staff_form.html", {"form": form})


# ---------------- NOTICE ----------------

@login_required
def notice_list(request):
    notices = SocietyNotice.objects.all().order_by("-createdAt")
    return render(request, "society/notice_list.html", {"notices": notices})


@login_required
@role_required("chairman", "super_admin")
def add_notice(request):
    form = NoticeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.postedBy = request.user
        obj.save()
        messages.success(request, "Notice posted.")
        return redirect("society:notice_list")

    return render(request, "society/notice_form.html", {"form": form})