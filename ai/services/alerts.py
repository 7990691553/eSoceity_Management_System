from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Count, Q

from society.models import Visitor, Delivery, ChildEntryLog, StaffAttendance


def build_alert(severity, title, message, action=None, module=None):
    """
    Standard structure for each smart alert.
    """
    return {
        "severity": severity,   # info / warning / danger
        "title": title,
        "message": message,
        "action": action or "",
        "module": module or "",
    }


def get_existing_field(model, candidates):
    """
    Return the first field name that exists in the model.
    """
    model_fields = [field.name for field in model._meta.get_fields()]
    for field_name in candidates:
        if field_name in model_fields:
            return field_name
    return None


def get_today_count(model, date_field):
    """
    Count records created today using a given datetime/date field.
    """
    today = now().date()
    return model.objects.filter(**{f"{date_field}__date": today}).count()


def get_yesterday_count(model, date_field):
    """
    Count records created yesterday using a given datetime/date field.
    """
    yesterday = now().date() - timedelta(days=1)
    return model.objects.filter(**{f"{date_field}__date": yesterday}).count()


def get_last_7_days_average(model, date_field):
    """
    Average daily count for previous 7 days excluding today.
    """
    today = now().date()
    start_date = today - timedelta(days=7)
    end_date = today - timedelta(days=1)

    total = model.objects.filter(
        **{f"{date_field}__date__range": [start_date, end_date]}
    ).count()

    return round(total / 7, 1)


def detect_high_visitor_traffic():
    alerts = []

    visitor_date_field = get_existing_field(Visitor, ["createdAt", "created_at", "dateCreated"])
    if not visitor_date_field:
        return alerts

    visitors_today = get_today_count(Visitor, visitor_date_field)
    visitors_yesterday = get_yesterday_count(Visitor, visitor_date_field)
    visitor_avg_7 = get_last_7_days_average(Visitor, visitor_date_field)

    if visitors_today > visitor_avg_7 and visitors_today > visitors_yesterday:
        alerts.append(build_alert(
            severity="warning",
            title="High Visitor Traffic",
            message=(
                f"Visitor activity is above normal today. "
                f"{visitors_today} visitors were recorded today, compared to "
                f"{visitors_yesterday} yesterday and an average of {visitor_avg_7} over the last 7 days."
            ),
            action="Security should watch gate activity closely.",
            module="visitor"
        ))

    return alerts


def detect_high_delivery_traffic():
    alerts = []

    delivery_date_field = get_existing_field(Delivery, ["createdAt", "created_at", "dateCreated"])
    if not delivery_date_field:
        return alerts

    deliveries_today = get_today_count(Delivery, delivery_date_field)
    deliveries_yesterday = get_yesterday_count(Delivery, delivery_date_field)
    delivery_avg_7 = get_last_7_days_average(Delivery, delivery_date_field)

    if deliveries_today > delivery_avg_7 and deliveries_today > deliveries_yesterday:
        alerts.append(build_alert(
            severity="warning",
            title="High Delivery Traffic",
            message=(
                f"Delivery activity is above recent trend today. "
                f"{deliveries_today} deliveries were recorded today, compared to "
                f"{deliveries_yesterday} yesterday and an average of {delivery_avg_7} over the last 7 days."
            ),
            action="Prepare for higher parcel handling workload.",
            module="delivery"
        ))

    return alerts


def detect_repeated_visitors():
    """
    Detect repeated visitor names/phones on same day.
    Works only if a suitable identity field exists.
    """
    alerts = []

    visitor_date_field = get_existing_field(Visitor, ["createdAt", "created_at", "dateCreated"])
    identity_field = get_existing_field(
        Visitor,
        ["visitorName", "name", "full_name", "visitor_name", "contact_no", "phone", "mobile"]
    )

    if not visitor_date_field or not identity_field:
        return alerts

    today = now().date()

    repeated = (
        Visitor.objects
        .filter(**{f"{visitor_date_field}__date": today})
        .values(identity_field)
        .annotate(total=Count("id"))
        .filter(total__gte=3)
        .order_by("-total")
    )

    for item in repeated[:3]:
        identity_value = item.get(identity_field)
        total = item.get("total", 0)

        alerts.append(build_alert(
            severity="info",
            title="Repeated Visitor Pattern",
            message=(
                f"'{identity_value}' appears {total} times in today's visitor records. "
                f"This may be normal, but repeated entries should be verified."
            ),
            action="Check whether the entries belong to the same resident or flat.",
            module="visitor"
        ))

    return alerts


def detect_old_pending_deliveries():
    """
    Detect deliveries that are pending/uncollected for too long.
    This depends on your Delivery model having a status-like field.
    """
    alerts = []

    delivery_date_field = get_existing_field(Delivery, ["createdAt", "created_at", "dateCreated"])
    status_field = get_existing_field(
        Delivery,
        ["status", "deliveryStatus", "delivery_status", "state"]
    )

    if not delivery_date_field or not status_field:
        return alerts

    cutoff_date = now() - timedelta(days=1)

    pending_keywords = ["pending", "received", "stored", "uncollected"]

    query = Q()
    for keyword in pending_keywords:
        query |= Q(**{f"{status_field}__iexact": keyword})

    old_pending_count = Delivery.objects.filter(
        query,
        **{f"{delivery_date_field}__lt": cutoff_date}
    ).count()

    if old_pending_count > 0:
        alerts.append(build_alert(
            severity="warning",
            title="Old Pending Deliveries",
            message=(
                f"{old_pending_count} delivery record(s) appear to be pending or uncollected "
                f"for more than 24 hours."
            ),
            action="Check parcel storage and notify residents for collection.",
            module="delivery"
        ))

    return alerts


def detect_staff_missing_checkout():
    """
    Detect staff records with check-in but no check-out.
    Uses a proper date field instead of applying __date to a TimeField.
    """
    alerts = []

    date_field = get_existing_field(
        StaffAttendance,
        ["attendanceDate", "date", "createdAt", "created_at"]
    )
    in_field = get_existing_field(
        StaffAttendance,
        ["staffInTime", "staff_in_time", "in_time"]
    )
    out_field = get_existing_field(
        StaffAttendance,
        ["staffOutTime", "staff_out_time", "out_time"]
    )
    name_field = get_existing_field(
        StaffAttendance,
        ["staffName", "staff_name", "name"]
    )

    if not in_field or not out_field:
        return alerts

    today = now().date()

    filters = {
        f"{out_field}__isnull": True
    }

    # Use a real date field if present
    if date_field:
        filters[f"{date_field}"] = today

    queryset = StaffAttendance.objects.filter(**filters)

    # If there is a check-in field, ensure it is present
    if in_field:
        queryset = queryset.exclude(**{f"{in_field}__isnull": True})

    missing_count = queryset.count()

    if missing_count > 0:
        staff_names = []
        if name_field:
            staff_names = list(queryset.values_list(name_field, flat=True)[:5])

        extra_text = ""
        if staff_names:
            extra_text = " Example: " + ", ".join(str(name) for name in staff_names if name)

        alerts.append(build_alert(
            severity="warning",
            title="Incomplete Staff Attendance",
            message=(
                f"{missing_count} staff attendance record(s) have check-in but no check-out for today."
                f"{extra_text}"
            ),
            action="Verify whether staff have left or checkout was missed.",
            module="staff"
        ))

    return alerts

def detect_child_movement_mismatch():
    """
    Detect incomplete child movement logs.
    Safe version that uses a real date/datetime field only.
    """
    alerts = []

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
        return alerts

    today = now().date()

    # Build queryset safely depending on field type
    model_field = ChildEntryLog._meta.get_field(date_field)

    if model_field.get_internal_type() == "DateTimeField":
        base_qs = ChildEntryLog.objects.filter(**{f"{date_field}__date": today})
    else:
        base_qs = ChildEntryLog.objects.filter(**{date_field: today})

    logs = (
        base_qs
        .values(child_field, type_field)
        .annotate(total=Count("id"))
    )

    child_summary = {}

    for row in logs:
        child_id = row[child_field]
        movement_type = str(row[type_field]).lower()
        total = row["total"]

        if child_id not in child_summary:
            child_summary[child_id] = {"entry": 0, "exit": 0}

        if "entry" in movement_type or movement_type == "in":
            child_summary[child_id]["entry"] += total
        elif "exit" in movement_type or movement_type == "out":
            child_summary[child_id]["exit"] += total

    mismatch_count = 0
    for _, data in child_summary.items():
        if data["entry"] != data["exit"]:
            mismatch_count += 1

    if mismatch_count > 0:
        alerts.append(build_alert(
            severity="danger",
            title="Child Movement Mismatch",
            message=(
                f"{mismatch_count} child record(s) show unmatched entry/exit movement for today."
            ),
            action="Review child monitoring logs immediately.",
            module="child"
        ))

    return alerts


def generate_smart_alerts():
    """
    Main function for AI dashboard.
    Returns a combined list of smart alerts.
    """
    alerts = []

    alerts.extend(detect_high_visitor_traffic())
    alerts.extend(detect_high_delivery_traffic())
    alerts.extend(detect_repeated_visitors())
    alerts.extend(detect_old_pending_deliveries())
    alerts.extend(detect_staff_missing_checkout())
    alerts.extend(detect_child_movement_mismatch())

    # Sort alerts by severity importance
    severity_order = {"danger": 1, "warning": 2, "info": 3}
    alerts = sorted(alerts, key=lambda x: severity_order.get(x["severity"], 99))

    return alerts