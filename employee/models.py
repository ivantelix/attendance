from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Employee(models.Model):
    names = models.CharField(max_length=100)
    document = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    position = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    check_in_time = models.TimeField(default=timezone.now)
    check_out_time = models.TimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.names} ({self.position})"
    
    class Meta:
        ordering = ['names']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees' 