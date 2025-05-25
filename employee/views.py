from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from .models import Employee
from .forms import EmployeeForm, UserForm
from attendance.models import Attendance

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee/list.html', {'employees': employees})

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employee/detail.html', {'employee': employee})

@login_required
@transaction.atomic
def employee_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        employee_form = EmployeeForm(request.POST)
        
        if user_form.is_valid() and employee_form.is_valid():
            try:
                # Create user with transaction to ensure data integrity
                user = user_form.save(commit=False)
                password = user_form.cleaned_data['password']
                user.set_password(password)
                user.save()
                
                # Create employee
                employee = employee_form.save(commit=False)
                employee.user = user
                employee.save()
                
                messages.success(request, f'Employee {employee.names} created successfully!')
                return redirect('employee_list')
            except Exception as e:
                messages.error(request, f'Error creating employee: {str(e)}')
    else:
        user_form = UserForm()
        employee_form = EmployeeForm()
    
    return render(request, 'employee/form.html', {
        'user_form': user_form,
        'employee_form': employee_form,
        'title': 'Create Employee'
    })

@login_required
@transaction.atomic
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    user = employee.user
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        employee_form = EmployeeForm(request.POST, instance=employee)
        
        if user_form.is_valid() and employee_form.is_valid():
            try:
                # Update user with transaction to ensure data integrity
                user = user_form.save(commit=False)
                password = user_form.cleaned_data.get('password')
                if password:
                    user.set_password(password)
                user.save()
                
                # Update employee
                employee = employee_form.save()
                
                messages.success(request, f'Employee {employee.names} updated successfully!')
                return redirect('employee_list')
            except Exception as e:
                messages.error(request, f'Error updating employee: {str(e)}')
    else:
        user_form = UserForm(instance=user)
        employee_form = EmployeeForm(instance=employee)
    
    return render(request, 'employee/form.html', {
        'user_form': user_form,
        'employee_form': employee_form,
        'employee': employee,
        'title': 'Edit Employee'
    })

@login_required
@transaction.atomic
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        try:
            user = employee.user
            # Get the employee's name before deletion
            employee_name = employee.names
            
            # Delete associated attendance records
            Attendance.objects.filter(user=user).delete()
            
            # Delete the employee and the user
            employee.delete()
            user.delete()
            
            messages.success(request, f'Employee {employee_name} deleted successfully!')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error deleting employee: {str(e)}')
            return redirect('employee_detail', pk=pk)
    
    return render(request, 'employee/delete.html', {'employee': employee}) 