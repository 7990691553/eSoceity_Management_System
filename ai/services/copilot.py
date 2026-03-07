from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Q

from society.models import Visitor, Delivery, StaffAttendance, ChildEntryLog, SocietyNotice
from ai.services.alerts import generate_smart_alerts
from ai.services.risk_analysis import generate_risk_watchlist
from ai.services.health_score import generate_society_health_score


# -----------------------------
# Generic helpers
# -----------------------------

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


def get_today_count(model, date_candidates):
    date_field = get_existing_field(model, date_candidates)
    if not date_field:
        return 0

    today_filter = build_today_filter(model, date_field)
    if not today_filter:
        return 0

    return model.objects.filter(**today_filter).count()


def get_notice_count():
    """
    Simple notice count.
    If later you add status/expiry/target role, this can be improved.
    """
    return SocietyNotice.objects.count()


def get_pending_visitors_count():
    status_field = get_existing_field(Visitor, ["status", "visitorStatus", "visitor_status"])
    if not status_field:
        return 0

    return Visitor.objects.filter(
        Q(**{f"{status_field}__iexact": "pending"}) |
        Q(**{f"{status_field}__iexact": "requested"}) |
        Q(**{f"{status_field}__iexact": "waiting"})
    ).count()


def get_pending_deliveries_count():
    status_field = get_existing_field(Delivery, ["status", "deliveryStatus", "delivery_status", "state"])
    if not status_field:
        return 0

    return Delivery.objects.filter(
        Q(**{f"{status_field}__iexact": "pending"}) |
        Q(**{f"{status_field}__iexact": "received"}) |
        Q(**{f"{status_field}__iexact": "stored"}) |
        Q(**{f"{status_field}__iexact": "uncollected"})
    ).count()


def get_incomplete_staff_count():
    date_field = get_existing_field(StaffAttendance, ["attendanceDate", "date", "createdAt", "created_at"])
    in_field = get_existing_field(StaffAttendance, ["staffInTime", "staff_in_time", "in_time"])
    out_field = get_existing_field(StaffAttendance, ["staffOutTime", "staff_out_time", "out_time"])

    if not in_field or not out_field:
        return 0

    filters = {f"{out_field}__isnull": True}
    if date_field:
        filters[date_field] = now().date()

    return StaffAttendance.objects.filter(**filters).exclude(
        **{f"{in_field}__isnull": True}
    ).count()


def get_child_mismatch_count():
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
        return 0

    field_type = get_field_type(ChildEntryLog, date_field)
    today = now().date()

    if field_type == "DateTimeField":
        qs = ChildEntryLog.objects.filter(**{f"{date_field}__date": today})
    elif field_type == "DateField":
        qs = ChildEntryLog.objects.filter(**{date_field: today})
    else:
        return 0

    summary = {}

    for row in qs.values(child_field, type_field):
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

    return mismatch_count


def make_status_cards(items):
    return [{"label": label, "value": value} for label, value in items]


def clean_tasks(tasks, limit=3):
    cleaned = [task for task in tasks if task]
    return cleaned[:limit]


# -----------------------------
# Role builders
# -----------------------------

def build_super_admin_copilot(user):
    visitors_today = get_today_count(Visitor, ["createdAt", "created_at", "dateCreated"])
    deliveries_today = get_today_count(Delivery, ["createdAt", "created_at", "dateCreated"])
    alerts = generate_smart_alerts()
    watchlist = generate_risk_watchlist()
    health = generate_society_health_score(alert_count=len(alerts))
    incomplete_staff = get_incomplete_staff_count()
    child_mismatch = get_child_mismatch_count()
    notices = get_notice_count()

    summary = (
        f"Society health is {health['score']}/100 ({health['status']}). "
        f"Today there are {visitors_today} visitors, {deliveries_today} deliveries, "
        f"{len(alerts)} active alerts, and {len(watchlist)} watchlist item(s)."
    )

    tasks = []
    if health["score"] < 75:
        tasks.append("Review overall operations because society health needs attention.")
    if get_pending_deliveries_count() > 0:
        tasks.append("Check pending deliveries and parcel backlog.")
    if incomplete_staff > 0:
        tasks.append("Resolve incomplete staff attendance records.")
    if child_mismatch > 0:
        tasks.append("Review unmatched child movement logs.")
    if len(watchlist) > 0:
        tasks.append("Inspect high and medium risk items in the watchlist.")

    recommended_action = "Review the highest risk operational issue first."
    if get_pending_deliveries_count() > 0:
        recommended_action = "Start by reviewing delayed or pending deliveries."
    elif incomplete_staff > 0:
        recommended_action = "Start by resolving incomplete staff attendance."
    elif len(watchlist) > 0:
        recommended_action = "Start by checking the top risk watchlist items."

    tips = [
        "Use the AI dashboard to inspect alerts, risks, and health score together.",
        "Monitor repeated visitor and delivery patterns for unusual trends.",
        "Check notices if society-wide communication may be needed."
    ]

    return {
        "role": "super_admin",
        "heading": "eSociety Copilot — Operations Overview",
        "summary": summary,
        "priority_tasks": clean_tasks(tasks),
        "recommended_action": recommended_action,
        "status_cards": make_status_cards([
            ("Health Score", health["score"]),
            ("Alerts", len(alerts)),
            ("Risk Items", len(watchlist)),
            ("Notices", notices),
        ]),
        "tips": tips,
    }


def build_chairman_copilot(user):
    alerts = generate_smart_alerts()
    watchlist = generate_risk_watchlist()
    health = generate_society_health_score(alert_count=len(alerts))
    pending_visitors = get_pending_visitors_count()
    pending_deliveries = get_pending_deliveries_count()
    notices = get_notice_count()

    summary = (
        f"Society health is {health['score']}/100 ({health['status']}). "
        f"There are {pending_visitors} pending visitor request(s), "
        f"{pending_deliveries} pending delivery item(s), and {len(alerts)} active alert(s)."
    )

    tasks = []
    if health["score"] < 75:
        tasks.append("Review operational pressure and management priorities.")
    if pending_visitors > 0:
        tasks.append("Check whether visitor approval flow needs management attention.")
    if pending_deliveries > 0:
        tasks.append("Review parcel backlog and collection delays.")
    if len(watchlist) > 0:
        tasks.append("Inspect repeated risk patterns and decide on corrective action.")
    if notices == 0:
        tasks.append("Consider whether any operational notice should be issued today.")

    recommended_action = "Review pending operations and decide whether society-wide guidance is needed."
    if len(watchlist) > 0:
        recommended_action = "Review current risk patterns and take management action where needed."

    tips = [
        "Use notices strategically if repeated issues continue.",
        "Health score below 75 usually means at least one operational area needs attention.",
        "Watch repeated visitor and delivery patterns over multiple days."
    ]

    return {
        "role": "chairman",
        "heading": "eSociety Copilot — Management Assistant",
        "summary": summary,
        "priority_tasks": clean_tasks(tasks),
        "recommended_action": recommended_action,
        "status_cards": make_status_cards([
            ("Health Score", health["score"]),
            ("Pending Visitors", pending_visitors),
            ("Pending Deliveries", pending_deliveries),
            ("Alerts", len(alerts)),
        ]),
        "tips": tips,
    }


def build_security_copilot(user):
    pending_visitors = get_pending_visitors_count()
    pending_deliveries = get_pending_deliveries_count()
    alerts = generate_smart_alerts()
    watchlist = generate_risk_watchlist()
    child_mismatch = get_child_mismatch_count()

    security_watch_items = [
        item for item in watchlist
        if item.get("module") in ["visitor", "delivery", "child"]
    ]

    summary = (
        f"You currently have {pending_visitors} pending visitor request(s), "
        f"{pending_deliveries} delivery item(s) needing attention, and "
        f"{len(security_watch_items)} risk-related item(s) relevant to security."
    )

    tasks = []
    if pending_visitors > 0:
        tasks.append("Review pending visitor approvals first.")
    if security_watch_items:
        tasks.append("Verify repeated visitor or risky watchlist items.")
    if pending_deliveries > 0:
        tasks.append("Check pending or uncollected deliveries.")
    if child_mismatch > 0:
        tasks.append("Review child movement mismatch records.")

    recommended_action = "Clear the visitor queue first."
    if pending_visitors == 0 and pending_deliveries > 0:
        recommended_action = "Review pending deliveries next."
    elif pending_visitors == 0 and not security_watch_items and child_mismatch > 0:
        recommended_action = "Check child monitoring records."

    tips = [
        "Repeated visitor activity should be verified before entry is allowed.",
        "Pending deliveries older than one day should be reviewed.",
        "Use dashboard alerts to identify the most urgent gate issues."
    ]

    return {
        "role": "security",
        "heading": "eSociety Copilot — Gate Assistant",
        "summary": summary,
        "priority_tasks": clean_tasks(tasks),
        "recommended_action": recommended_action,
        "status_cards": make_status_cards([
            ("Pending Visitors", pending_visitors),
            ("Pending Deliveries", pending_deliveries),
            ("Security Risks", len(security_watch_items)),
            ("Child Issues", child_mismatch),
        ]),
        "tips": tips,
    }


def build_member_copilot(user):
    notices = get_notice_count()
    summary = (
        f"You have access to current society updates and notices. "
        f"There are {notices} notice record(s) available in the system."
    )

    tasks = [
        "Check the latest society notices.",
        "Review your visitor and delivery updates from your dashboard.",
        "Stay updated on any operational announcements."
    ]

    recommended_action = "Start by checking important notices and your latest updates."

    tips = [
        "Use your dashboard to track visitor and delivery updates.",
        "Pay attention to urgent notices related to maintenance or access.",
        "If you later link flats/units to users, Copilot can become fully personalized."
    ]

    return {
        "role": "member",
        "heading": "eSociety Copilot — Resident Assistant",
        "summary": summary,
        "priority_tasks": clean_tasks(tasks),
        "recommended_action": recommended_action,
        "status_cards": make_status_cards([
            ("Notices", notices),
            ("Visitor Updates", "-"),
            ("Delivery Updates", "-"),
            ("Status", "Active"),
        ]),
        "tips": tips,
    }


def build_helper_copilot(user):
    notices = get_notice_count()

    summary = (
        f"There are {notices} notice record(s) in the system. "
        f"Please stay updated with important society instructions and daily operational guidance."
    )

    tasks = [
        "Check important notices before starting work.",
        "Follow updated entry or movement instructions if any.",
        "Stay aware of any maintenance or access restrictions."
    ]

    recommended_action = "Start your day by checking active notices and instructions."

    tips = [
        "Important notices may contain access or timing updates.",
        "Follow society rules and instructions shown on the dashboard.",
        "Ask management if any notice is unclear."
    ]

    return {
        "role": "helper",
        "heading": "eSociety Copilot — Daily Guidance Assistant",
        "summary": summary,
        "priority_tasks": clean_tasks(tasks),
        "recommended_action": recommended_action,
        "status_cards": make_status_cards([
            ("Notices", notices),
            ("Access Status", "Check"),
            ("Instructions", "Available"),
            ("Today", "Active"),
        ]),
        "tips": tips,
    }


# -----------------------------
# Main dispatcher
# -----------------------------

def generate_copilot_context(user):
    role = getattr(user, "role", "").strip().lower()

    if role == "super_admin":
        return build_super_admin_copilot(user)
    elif role == "chairman":
        return build_chairman_copilot(user)
    elif role == "security":
        return build_security_copilot(user)
    elif role == "member":
        return build_member_copilot(user)
    elif role == "helper":
        return build_helper_copilot(user)

    return {
        "role": "unknown",
        "heading": "eSociety Copilot",
        "summary": "Your role-specific assistant is not configured yet.",
        "priority_tasks": [],
        "recommended_action": "Please contact the administrator.",
        "status_cards": [],
        "tips": [],
    }