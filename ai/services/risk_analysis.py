from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Count, Q

from society.models import Visitor, Delivery


def build_watch_item(risk_level, title, message, score, module=None, suggestion=None):
    return {
        "risk_level": risk_level,   # low / medium / high
        "title": title,
        "message": message,
        "score": score,
        "module": module or "",
        "suggestion": suggestion or "",
    }


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


def get_repeated_entries_today(model, date_field, identity_field, min_count=3):
    today_filter = build_today_filter(model, date_field)
    if not today_filter:
        return []

    return list(
        model.objects
        .filter(**today_filter)
        .values(identity_field)
        .annotate(total=Count("id"))
        .filter(total__gte=min_count)
        .order_by("-total")
    )


def analyze_visitor_risk():
    watchlist = []

    date_field = get_existing_field(Visitor, ["createdAt", "created_at", "dateCreated"])
    name_field = get_existing_field(Visitor, ["visitorName", "visitor_name", "name", "full_name"])
    phone_field = get_existing_field(Visitor, ["contact_no", "phone", "mobile"])
    purpose_field = get_existing_field(Visitor, ["purpose", "visitPurpose", "visit_purpose"])
    status_field = get_existing_field(Visitor, ["status", "visitorStatus", "visitor_status"])

    if not date_field:
        return watchlist

    identity_field = name_field or phone_field
    if not identity_field:
        return watchlist

    repeated_visitors = get_repeated_entries_today(Visitor, date_field, identity_field, min_count=3)

    for item in repeated_visitors[:5]:
        identity_value = item.get(identity_field)
        total = item.get("total", 0)

        score = 0
        if total >= 3:
            score += 2
        if total >= 5:
            score += 2

        risk_level = "medium"
        if score >= 4:
            risk_level = "high"

        watchlist.append(build_watch_item(
            risk_level=risk_level,
            title="Repeated Visitor Activity",
            message=f"Visitor '{identity_value}' appears {total} times in today's records.",
            score=score,
            module="visitor",
            suggestion="Security should verify whether repeated entries are expected."
        ))

    if status_field:
        denied_count = Visitor.objects.filter(
            **{f"{status_field}__iexact": "denied"}
        ).count()

        if denied_count >= 3:
            watchlist.append(build_watch_item(
                risk_level="medium",
                title="Multiple Denied Visitor Records",
                message=f"{denied_count} denied visitor record(s) found in the system.",
                score=3,
                module="visitor",
                suggestion="Review denied visitor patterns for repeated suspicious attempts."
            ))

    return watchlist


def analyze_delivery_risk():
    watchlist = []

    date_field = get_existing_field(Delivery, ["createdAt", "created_at", "dateCreated"])
    status_field = get_existing_field(Delivery, ["status", "deliveryStatus", "delivery_status", "state"])
    flat_field = get_existing_field(Delivery, ["flatNo", "flat_no", "flat", "unitNo", "unit_no", "unit"])
    courier_field = get_existing_field(Delivery, ["deliveryFrom", "courier_name", "courier", "source"])

    if not date_field:
        return watchlist

    if status_field:
        cutoff_24 = now() - timedelta(days=1)
        cutoff_48 = now() - timedelta(days=2)

        old_pending_24 = Delivery.objects.filter(
            Q(**{f"{status_field}__iexact": "pending"}) |
            Q(**{f"{status_field}__iexact": "received"}) |
            Q(**{f"{status_field}__iexact": "stored"}) |
            Q(**{f"{status_field}__iexact": "uncollected"}),
            **{f"{date_field}__lt": cutoff_24}
        ).count()

        old_pending_48 = Delivery.objects.filter(
            Q(**{f"{status_field}__iexact": "pending"}) |
            Q(**{f"{status_field}__iexact": "received"}) |
            Q(**{f"{status_field}__iexact": "stored"}) |
            Q(**{f"{status_field}__iexact": "uncollected"}),
            **{f"{date_field}__lt": cutoff_48}
        ).count()

        if old_pending_24 > 0:
            score = 2
            risk_level = "medium"

            if old_pending_48 > 0:
                score = 4
                risk_level = "high"

            watchlist.append(build_watch_item(
                risk_level=risk_level,
                title="Delayed Delivery Collection",
                message=f"{old_pending_24} delivery record(s) appear pending for more than 24 hours.",
                score=score,
                module="delivery",
                suggestion="Notify residents to collect pending parcels."
            ))

    if flat_field:
        repeated_flats = get_repeated_entries_today(Delivery, date_field, flat_field, min_count=4)

        for item in repeated_flats[:5]:
            flat_value = item.get(flat_field)
            total = item.get("total", 0)

            score = 2 if total >= 4 else 1
            risk_level = "medium" if total >= 4 else "low"

            if total >= 6:
                score = 4
                risk_level = "high"

            watchlist.append(build_watch_item(
                risk_level=risk_level,
                title="Unusual Delivery Volume",
                message=f"Flat/Unit '{flat_value}' has {total} delivery records today.",
                score=score,
                module="delivery",
                suggestion="Check if high parcel volume is expected for this unit."
            ))

    return watchlist


def generate_risk_watchlist():
    watchlist = []
    watchlist.extend(analyze_visitor_risk())
    watchlist.extend(analyze_delivery_risk())

    risk_order = {"high": 1, "medium": 2, "low": 3}
    watchlist = sorted(watchlist, key=lambda x: (risk_order.get(x["risk_level"], 99), -x["score"]))

    return watchlist