from django.db import models

# Create your models here.

class AIInsight(models.Model):

    generated_at = models.DateTimeField(auto_now_add=True)

    visitors_today = models.IntegerField(default=0)
    deliveries_today = models.IntegerField(default=0)

    insight_message = models.TextField()

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"Insight generated at {self.generated_at}"