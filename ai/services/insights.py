from datetime import timedelta
from django.utils.timezone import now
from society.models import Visitor, Delivery
from ai.models import AIInsight


def percentage_change(today_count, previous_count):
    """
    Safely calculate percentage change.
    """
    if previous_count == 0:
        if today_count == 0:
            return 0
        return 100
    return round(((today_count - previous_count) / previous_count) * 100, 1)


def get_last_7_days_average(model, date_field):
    """
    Returns average daily count over the previous 7 days
    excluding today.
    """
    today = now().date()
    start_date = today - timedelta(days=7)
    end_date = today - timedelta(days=1)

    total = model.objects.filter(
        **{f"{date_field}__date__range": [start_date, end_date]}
    ).count()

    # Avoid division by zero; always divide by 7 for a simple stable average
    return round(total / 7, 1)


def generate_ai_insight():
    today = now().date()
    yesterday = today - timedelta(days=1)

    # --- Today counts ---
    visitors_today = Visitor.objects.filter(createdAt__date=today).count()
    deliveries_today = Delivery.objects.filter(createdAt__date=today).count()

    # --- Yesterday counts ---
    visitors_yesterday = Visitor.objects.filter(createdAt__date=yesterday).count()
    deliveries_yesterday = Delivery.objects.filter(createdAt__date=yesterday).count()

    # --- Last 7 days averages ---
    visitor_avg_7_days = get_last_7_days_average(Visitor, "createdAt")
    delivery_avg_7_days = get_last_7_days_average(Delivery, "createdAt")

    # --- Percentage changes ---
    visitor_change = percentage_change(visitors_today, visitors_yesterday)
    delivery_change = percentage_change(deliveries_today, deliveries_yesterday)

    messages = []

    # Visitor insight
    if visitors_today > visitor_avg_7_days and visitors_today > visitors_yesterday:
        messages.append(
            f"Visitor activity is higher than usual today. "
            f"There are {visitors_today} visitors today, compared to {visitors_yesterday} yesterday."
        )
    elif visitors_today < visitors_yesterday:
        messages.append(
            f"Visitor activity has decreased today. "
            f"There are {visitors_today} visitors today, down from {visitors_yesterday} yesterday."
        )
    else:
        messages.append(
            f"Visitor activity is stable today with {visitors_today} entries."
        )

    # Delivery insight
    if deliveries_today > delivery_avg_7_days and deliveries_today > deliveries_yesterday:
        messages.append(
            f"Delivery activity is above the recent trend. "
            f"There are {deliveries_today} deliveries today, compared to {deliveries_yesterday} yesterday."
        )
    elif deliveries_today < deliveries_yesterday:
        messages.append(
            f"Delivery activity is lower today with {deliveries_today} deliveries, "
            f"down from {deliveries_yesterday} yesterday."
        )
    else:
        messages.append(
            f"Delivery activity remains steady today with {deliveries_today} deliveries."
        )

    # Combined operational summary
    if visitors_today > visitor_avg_7_days and deliveries_today > delivery_avg_7_days:
        messages.append("Overall society activity is busier than the recent 7-day average.")
    elif visitors_today == 0 and deliveries_today == 0:
        messages.append("Society activity is very low today.")
    else:
        messages.append("Overall society operations appear normal today.")

    insight_message = " ".join(messages)

    insight = AIInsight.objects.create(
        visitors_today=visitors_today,
        deliveries_today=deliveries_today,
        insight_message=insight_message,
    )

    return insight