from django import forms
from .models import Attendance
from django.contrib.auth.models import User

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['user', 'clock_in', 'clock_out', 'description']
        widgets = {
            'clock_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'clock_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            }) 