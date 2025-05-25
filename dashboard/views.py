from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from attendance.models import Attendance
from employee.models import Employee
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard(request):
    # Get counts for dashboard stats
    total_employees = Employee.objects.count()
    total_users = User.objects.count()
    
    # Get today's attendance
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(
        clock_in__date=today
    ).count()
    
    # Get last 7 days attendance
    last_week = today - timedelta(days=7)
    weekly_attendance = Attendance.objects.filter(
        clock_in__date__gte=last_week,
        clock_in__date__lte=today
    ).count()
    
    context = {
        'total_employees': total_employees,
        'total_users': total_users,
        'today_attendance': today_attendance,
        'weekly_attendance': weekly_attendance,
    }
    return render(request, 'dashboard/index.html', context) 