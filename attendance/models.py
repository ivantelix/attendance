from django.db import models
from django.contrib.auth.models import User

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.clock_in}"
    
    @property
    def duration(self):
        if self.clock_in and self.clock_out:
            return self.clock_out - self.clock_in
        return None
    
    @property
    def employee_name(self):
        if hasattr(self.user, 'employee'):
            return self.user.employee.names
        return self.user.username
        
    class Meta:
        ordering = ['-clock_in']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances' 