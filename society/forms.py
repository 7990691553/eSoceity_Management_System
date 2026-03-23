from django import forms
from .models import Visitor, Delivery, Child, StaffAttendance, SocietyNotice, VisitorEntryLog, ChildEntryLog, DeliveryLog, Complaint

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            "visitorName",
            "visitorType",
            "visitPurpose",
            "priorPermission",
            "memberId",
        ]
        widgets = {
            "visitorName": forms.TextInput(attrs={"class": "input", "placeholder": "Visitor name"}),
            "visitorType": forms.Select(attrs={"class": "input"}),
            "visitPurpose": forms.TextInput(attrs={"class": "input", "placeholder": "Purpose (optional)"}),
            "priorPermission": forms.CheckboxInput(attrs={"class": "checkbox"}),
            "memberId": forms.Select(attrs={"class": "input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally show only active members (safe)
        self.fields["memberId"].queryset = self.fields["memberId"].queryset.filter(is_active=True)


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            "deliveryPerson",
            "deliveryAllowed",
            "memberId",
        ]
        widgets = {
            "deliveryPerson": forms.TextInput(attrs={"class": "input", "placeholder": "Delivery person name"}),
            "deliveryAllowed": forms.CheckboxInput(attrs={"class": "checkbox"}),
            "memberId": forms.Select(attrs={"class": "input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["memberId"].queryset = self.fields["memberId"].queryset.filter(is_active=True)


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        # parentId is filled in views.py for member role
        fields = [
            "childName",
            "childAge",
            "childPhoto",
        ]
        widgets = {
            "childName": forms.TextInput(attrs={"class": "input", "placeholder": "Child name"}),
            "childAge": forms.NumberInput(attrs={"class": "input", "placeholder": "Age"}),
            "childPhoto": forms.ClearableFileInput(attrs={"class": "input"}),
        }

    def clean_childAge(self):
        age = self.cleaned_data.get("childAge")
        if age is None:
            return age
        if age < 0 or age > 18:
            raise forms.ValidationError("Child age must be between 0 and 18.")
        return age

class ChildAdminForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ["childName", "childAge", "childPhoto", "parentId"]
        widgets = {
            "childName": forms.TextInput(attrs={"class": "input", "placeholder": "Child name"}),
            "childAge": forms.NumberInput(attrs={"class": "input", "placeholder": "Age"}),
            "childPhoto": forms.ClearableFileInput(attrs={"class": "input"}),
            "parentId": forms.Select(attrs={"class": "input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # show only active members in dropdown (recommended)
        self.fields["parentId"].queryset = self.fields["parentId"].queryset.filter(
            is_active=True, role="member"
        )
        
class StaffAttendanceForm(forms.ModelForm):
    class Meta:
        model = StaffAttendance
        fields = [
            "staffName",
            "staffRole",
            "attendanceDate",
            "staffInTime",
            "staffOutTime",
        ]
        widgets = {
            "staffName": forms.TextInput(attrs={"class": "input", "placeholder": "Staff name"}),
            "staffRole": forms.Select(attrs={"class": "input"}),
            "attendanceDate": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "staffInTime": forms.TimeInput(attrs={"class": "input", "type": "time"}),
            "staffOutTime": forms.TimeInput(attrs={"class": "input", "type": "time"}),
        }

    def clean(self):
        cleaned = super().clean()
        in_time = cleaned.get("staffInTime")
        out_time = cleaned.get("staffOutTime")
        if in_time and out_time and out_time <= in_time:
            raise forms.ValidationError("Out time must be after In time.")
        return cleaned

class NoticeForm(forms.ModelForm):
    class Meta:
        model = SocietyNotice
        # postedBy is set in views.py; postedDate has default
        fields = [
            "noticeTitle",
            "noticeDescription",
        ]
        widgets = {
            "noticeTitle": forms.TextInput(attrs={"class": "input", "placeholder": "Notice title"}),
            "noticeDescription": forms.Textarea(attrs={"class": "input", "rows": 4, "placeholder": "Write notice..."}),
        }

class VisitorEntryLogForm(forms.ModelForm):
    class Meta:
        model = VisitorEntryLog
        fields = "__all__"
        widgets = {
            # replace these with your actual fields if needed
            # "field_name": forms.TextInput(attrs={"class": "input"}),
        }


class ChildEntryLogForm(forms.ModelForm):
    class Meta:
        model = ChildEntryLog
        fields = "__all__"
        widgets = {
            # add widgets if needed
        }

class DeliveryLogForm(forms.ModelForm):
    class Meta:
        model = DeliveryLog
        fields = ["deliveryId", "receivedTime", "collectedTime"]
        widgets = {
            "deliveryId":    forms.Select(attrs={"class": "input"}),
            "receivedTime":  forms.DateTimeInput(attrs={"class": "input", "type": "datetime-local"}),
            "collectedTime": forms.DateTimeInput(attrs={"class": "input", "type": "datetime-local"}),
        }

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["title", "description", "category", "priority"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "input",
                "placeholder": "Brief title of the issue"
            }),
            "description": forms.Textarea(attrs={
                "class": "input",
                "rows": 4,
                "placeholder": "Describe the issue in detail..."
            }),
            "category": forms.Select(attrs={"class": "input"}),
            "priority": forms.Select(attrs={"class": "input"}),
        }
 
 
class ComplaintUpdateForm(forms.ModelForm):
    """Used by admin/chairman to update status and add notes."""
    class Meta:
        model = Complaint
        fields = ["status", "adminNote"]
        widgets = {
            "status":    forms.Select(attrs={"class": "input"}),
            "adminNote": forms.Textarea(attrs={
                "class": "input",
                "rows": 3,
                "placeholder": "Add a note for the member (optional)..."
            }),
        }