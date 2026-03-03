from django import forms
from .models import Visitor, Delivery, Child, StaffAttendance, SocietyNotice

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