from django import forms
from django.contrib.auth.models import User
from .models import Employee

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, 
                              help_text="Leave empty if you don't want to change it.")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = ""

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['names', 'document', 'phone', 'position', 'check_in_time', 'check_out_time']
        
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            }) 