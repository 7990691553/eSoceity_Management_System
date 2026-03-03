from django.db import models
from django.conf import settings
from django.utils import timezone

#Create your models here.

# ---------------------------
# Visitor Module
# ---------------------------

class Visitor(models.Model):
    VISITOR_TYPE = (
        ("GUEST", "Guest"),
        ("SERVICE", "Service Provider"),
    )

    APPROVAL_STATUS = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    visitorName = models.CharField(max_length=30)
    visitorType = models.CharField(max_length=15, choices=VISITOR_TYPE)
    visitPurpose = models.CharField(max_length=100, null=True, blank=True)
    priorPermission = models.BooleanField(default=False)
    approvalStatus = models.CharField(max_length=10, choices=APPROVAL_STATUS, default="PENDING")

    # Target member (who the visitor is visiting)
    memberId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="visitors"
    )

    # Audit trail
    requestedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_requests_made",
        help_text="Usually security user who created the request.",
    )
    approvedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_requests_approved",
        help_text="Member/chairman who approved/rejected.",
    )
    approvedAt = models.DateTimeField(null=True, blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "visitor"
        ordering = ["-createdAt"]

    def __str__(self):
        return self.visitorName


class VisitorEntryLog(models.Model):
    visitorId = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name="entry_logs")

    entryTime = models.DateTimeField(default=timezone.now)
    exitTime = models.DateTimeField(null=True, blank=True)

    markedEntryBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_entries_marked",
    )
    markedExitBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_exits_marked",
    )

    class Meta:
        db_table = "visitor_entry_log"
        ordering = ["-entryTime"]

    def __str__(self):
        return self.visitorId.visitorName


# ---------------------------
# Delivery Module
# ---------------------------

class Delivery(models.Model):
    DELIVERY_STATUS = (
        ("PENDING", "Pending"),
        ("COLLECTED", "Collected"),
    )

    deliveryPerson = models.CharField(max_length=30)
    deliveryAllowed = models.BooleanField(default=True)
    deliveryStatus = models.CharField(max_length=10, choices=DELIVERY_STATUS, default="PENDING")
    storedAtSecurity = models.BooleanField(default=False)

    memberId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deliveries"
    )

    receivedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries_received",
    )
    collectedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries_collected",
    )

    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "delivery"
        ordering = ["-createdAt"]

    def __str__(self):
        return self.deliveryPerson


class DeliveryLog(models.Model):
    deliveryId = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name="logs")
    receivedTime = models.DateTimeField(default=timezone.now)
    collectedTime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "delivery_log"
        ordering = ["-receivedTime"]

    def __str__(self):
        return self.deliveryId.deliveryPerson


# ---------------------------
# Child Module
# ---------------------------

class ChildAgeLimit(models.Model):
    ageLimit = models.IntegerField()

    class Meta:
        db_table = "child_age_limit"

    def __str__(self):
        return str(self.ageLimit)


class Child(models.Model):
    childName = models.CharField(max_length=30)
    childAge = models.IntegerField()
    childPhoto = models.FileField(upload_to="child_photos/", null=True, blank=True)

    inTime = models.TimeField(null=True, blank=True)
    outTime = models.TimeField(null=True, blank=True)

    parentId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children"
    )

    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "child"
        ordering = ["childName"]

    def __str__(self):
        return self.childName


class ChildEntryLog(models.Model):
    childId = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="entry_logs")
    entryDateTime = models.DateTimeField(default=timezone.now)
    exitDateTime = models.DateTimeField(null=True, blank=True)

    markedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_entries_marked",
        help_text="Usually security user.",
    )

    class Meta:
        db_table = "child_entry_log"
        ordering = ["-entryDateTime"]

    def __str__(self):
        return f"{self.childId.childName} - {self.entryDateTime}"


# ---------------------------
# Staff Attendance
# ---------------------------

class StaffAttendance(models.Model):
    STAFF_ROLE = (
        ("SECURITY", "Security"),
        ("HELPER", "House Helper"),
    )

    staffName = models.CharField(max_length=30)
    staffRole = models.CharField(max_length=20, choices=STAFF_ROLE)
    attendanceDate = models.DateField(default=timezone.now)
    staffInTime = models.TimeField()
    staffOutTime = models.TimeField()

    markedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_attendance_marked",
    )

    class Meta:
        db_table = "staff_attendance"
        ordering = ["-attendanceDate"]

    def __str__(self):
        return self.staffName


# ---------------------------
# Notices
# ---------------------------

class SocietyNotice(models.Model):
    noticeTitle = models.CharField(max_length=100)
    noticeDescription = models.TextField()

    postedDate = models.DateField(default=timezone.now)

    postedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notices"
    )
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "society_notice"
        ordering = ["-createdAt"]

    def __str__(self):
        return self.noticeTitle


# ---------------------------
# Global Settings (Singleton)
# ---------------------------

class SocietySettings(models.Model):
    """
    Strong singleton: always keep ONE row with pk=1
    This avoids race conditions and is PostgreSQL-safe.
    """
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)

    deliveryAllowed = models.BooleanField(default=True)
    visitorAllowed = models.BooleanField(default=True)
    defaultAgeLimit = models.IntegerField(default=3)

    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "society_settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Society Settings"
