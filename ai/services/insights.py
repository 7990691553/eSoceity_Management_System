from django.utils.timezone import now
from society.models import Visitor, Delivery
from ai.models import AIInsight


def generate_ai_insight():

    today = now().date()

    visitors_today = Visitor.objects.filter(createdAt__date=today).count()
    deliveries_today = Delivery.objects.filter(createdAt__date=today).count()

    insight_message = "Normal society activity today."

    if visitors_today > 15:
        insight_message = "High visitor traffic detected today."

    if deliveries_today > 20:
        insight_message += " Delivery activity is also high."

    insight = AIInsight.objects.create(
        visitors_today=visitors_today,
        deliveries_today=deliveries_today,
        insight_message=insight_message
    )

    return insight