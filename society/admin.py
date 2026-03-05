from django.contrib import admin
from .models import (
    Visitor,
    VisitorEntryLog,
    Delivery,
    DeliveryLog,
    ChildAgeLimit,
    Child,
    ChildEntryLog,
    StaffAttendance,
    SocietyNotice,
    SocietySettings
)

admin.site.register(Visitor)
admin.site.register(VisitorEntryLog)

admin.site.register(Delivery)
admin.site.register(DeliveryLog)

admin.site.register(ChildAgeLimit)
admin.site.register(Child)
admin.site.register(ChildEntryLog)

admin.site.register(StaffAttendance)

admin.site.register(SocietyNotice)

admin.site.register(SocietySettings)
