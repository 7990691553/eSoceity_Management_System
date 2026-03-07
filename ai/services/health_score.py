from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Q

from society.models import Visitor, Delivery, StaffAttendance, ChildEntryLog


def get_existing_field(model, candidates):
    model_fields = [field.name for field in model._meta.get_fields()]
    for field_name in candidates:
        if field_name in model_fields:
            return field_name
    return None


def get_field_type(model, field_name):
    try:
        return model._meta.get_field(field_name).get_internal_type()
    except Exception:
        return None


def build_today_filter(model, field_name):
    today = now().date()
    field_type = get_field_type(model, field_name)

    if field_type == "DateTimeField":
        return {f"{field_name}__date": today}
    elif field_type == "DateField":
        return {field_name: today}
    return None


def get_today_count(model, date_field):
    today_filter = build_today_filter(model, date_field)
    if not today_filter:
        return 0
    return model.objects.filter(**today_filter).count()


def get_last_7_days_average(model, date_field):
    field_type = get_field_type(model, date_field)
    if not field_type:
        return 0

    today = now().date()
    start_date = today - timedelta(days=7)
    end_date = today - timedelta(days=1)

    if field_type == "DateTimeField":
        total = model.objects.filter(
            **{f"{date_field}__date__range": [start_date, end_date]}
        ).count()
    elif field_type == "DateField":
        total = model.objects.filter(
            **{f"{date_field}__range": [start_date, end_date]}
        ).count()
    else:
        return 0

    return round(total / 7, 1)


def clamp_score(score, minimum=0, maximum=20):
    return max(minimum, min(score, maximum))


def get_status_label(score):
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 50:
        return "Needs Attention"
    return "Critical"


def get_health_recommendation(score):
    if score >= 90:
        return "Society operations are running very smoothly. Maintain the current workflow."
    elif score >= 75:
        return "Operations are generally stable, but a few areas may need monitoring."
    elif score >= 50:
        return "Some operational issues need attention. Admin should review alerts and pending records."
    return "Multiple critical issues are affecting society operations. Immediate review is recommended."


def calculate_visitor_score():
    score = 20

    date_field = get_existing_field(Visitor, ["createdAt", "created_at", "dateCreated"])
    status_field = get_existing_field(Visitor, ["status", "visitorStatus", "visitor_status"])

    if not date_field:
        return {
            "title": "Visitor Management",
            "score": score,
            "message": "Visitor metrics unavailable."
        }

    visitors_today = get_today_count(Visitor, date_field)
    visitor_avg = get_last_7_days_average(Visitor, date_field)

    if visitor_avg > 0 and visitors_today > visitor_avg:
        score -= 4

    if visitor_avg > 0 and visitors_today >= (visitor_avg * 1.5):
        score -= 3

    if status_field:
        denied_count = Visitor.objects.filter(**{f"{status_field}__iexact": "denied"}).count()
        if denied_count >= 3:
            score -= 4
        elif denied_count > 0:
            score -= 2

    score = clamp_score(score)

    return {
        "title": "Visitor Management",
        "score": score,
        "message": f"Today's visitor flow is being evaluated against recent activity trends."
    }


def calculate_delivery_score():
    score = 20

    date_field = get_existing_field(Delivery, ["createdAt", "created_at", "dateCreated"])
    status_field = get_existing_field(Delivery, ["status", "deliveryStatus", "delivery_status", "state"])

    if not date_field:
        return {
            "title": "Delivery Handling",
            "score": score,
            "message": "Delivery metrics unavailable."
        }

    deliveries_today = get_today_count(Delivery, date_field)
    delivery_avg = get_last_7_days_average(Delivery, date_field)

    if delivery_avg > 0 and deliveries_today > delivery_avg:
        score -= 3

    if status_field:
        cutoff_24 = now() - timedelta(days=1)

        old_pending = Delivery.objects.filter(
            Q(**{f"{status_field}__iexact": "pending"}) |
            Q(**{f"{status_field}__iexact": "received"}) |
            Q(**{f"{status_field}__iexact": "stored"}) |
            Q(**{f"{status_field}__iexact": "uncollected"}),
            **{f"{date_field}__lt": cutoff_24}
        ).count()

        if old_pending >= 5:
            score -= 6
        elif old_pending > 0:
            score -= 3

    score = clamp_score(score)

    return {
        "title": "Delivery Handling",
        "score": score,
        "message": f"Delivery activity and pending parcel handling are included in this score."
    }


def calculate_staff_score():
    score = 20

    date_field = get_existing_field(StaffAttendance, ["attendanceDate", "date", "createdAt", "created_at"])
    in_field = get_existing_field(StaffAttendance, ["staffInTime", "staff_in_time", "in_time"])
    out_field = get_existing_field(StaffAttendance, ["staffOutTime", "staff_out_time", "out_time"])

    if not in_field or not out_field:
        return {
            "title": "Staff Attendance",
            "score": score,
            "message": "Staff attendance metrics unavailable."
        }

    filters = {f"{out_field}__isnull": True}
    if date_field:
        filters[date_field] = now().date()

    incomplete_count = StaffAttendance.objects.filter(**filters).exclude(
        **{f"{in_field}__isnull": True}
    ).count()

    if incomplete_count >= 5:
        score -= 8
    elif incomplete_count >= 3:
        score -= 5
    elif incomplete_count > 0:
        score -= 2

    score = clamp_score(score)

    return {
        "title": "Staff Attendance",
        "score": score,
        "message": "This score reflects incomplete check-out and attendance discipline."
    }


def calculate_child_score():
    score = 20

    child_field = get_existing_field(ChildEntryLog, ["child"])
    date_field = get_existing_field(
        ChildEntryLog,
        ["createdAt", "created_at", "entryDate", "logDate", "date", "timestamp"]
    )
    type_field = get_existing_field(
        ChildEntryLog,
        ["log_type", "movement_type", "status", "type"]
    )

    if not child_field or not date_field or not type_field:
        return {
            "title": "Child Monitoring",
            "score": score,
            "message": "Child monitoring metrics unavailable."
        }

    field_type = get_field_type(ChildEntryLog, date_field)
    today = now().date()

    if field_type == "DateTimeField":
        logs = ChildEntryLog.objects.filter(**{f"{date_field}__date": today})
    elif field_type == "DateField":
        logs = ChildEntryLog.objects.filter(**{date_field: today})
    else:
        logs = ChildEntryLog.objects.none()

    summary = {}

    for row in logs.values(child_field, type_field):
        child_id = row[child_field]
        movement_type = str(row[type_field]).lower()

        if child_id not in summary:
            summary[child_id] = {"entry": 0, "exit": 0}

        if "entry" in movement_type or movement_type == "in":
            summary[child_id]["entry"] += 1
        elif "exit" in movement_type or movement_type == "out":
            summary[child_id]["exit"] += 1

    mismatch_count = 0
    for _, movement in summary.items():
        if movement["entry"] != movement["exit"]:
            mismatch_count += 1

    if mismatch_count >= 3:
        score -= 8
    elif mismatch_count > 0:
        score -= 4

    score = clamp_score(score)

    return {
        "title": "Child Monitoring",
        "score": score,
        "message": "This score checks whether child movement records are balanced and complete."
    }


def calculate_alert_stability_score(alert_count):
    score = 20

    if alert_count >= 8:
        score -= 10
    elif alert_count >= 5:
        score -= 6
    elif alert_count >= 3:
        score -= 3

    score = clamp_score(score)

    return {
        "title": "Alert Stability",
        "score": score,
        "message": "This score reflects current operational pressure based on active AI alerts."
    }


def generate_society_health_score(alert_count=0):
    visitor_part = calculate_visitor_score()
    delivery_part = calculate_delivery_score()
    staff_part = calculate_staff_score()
    child_part = calculate_child_score()
    alert_part = calculate_alert_stability_score(alert_count)

    breakdown = [
        visitor_part,
        delivery_part,
        staff_part,
        child_part,
        alert_part,
    ]

    total_score = sum(item["score"] for item in breakdown)
    status = get_status_label(total_score)
    recommendation = get_health_recommendation(total_score)

    return {
        "score": total_score,
        "status": status,
        "recommendation": recommendation,
        "breakdown": breakdown,
    }