from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from .models import Attendance
from .forms import AttendanceForm
from employee.models import Employee
from django.http import JsonResponse

@login_required
def attendance_list(request):
    attendances = Attendance.objects.all()
    return render(request, 'attendance/list.html', {'attendances': attendances})

@login_required
def attendance_detail(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    return render(request, 'attendance/detail.html', {'attendance': attendance})

@login_required
@transaction.atomic
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            try:
                attendance = form.save()
                messages.success(request, 'Attendance record created successfully!')
                return redirect('attendance_list')
            except Exception as e:
                messages.error(request, f'Error creating attendance record: {str(e)}')
    else:
        form = AttendanceForm()
    
    return render(request, 'attendance/form.html', {
        'form': form,
        'title': 'Create Attendance Record'
    })

@login_required
@transaction.atomic
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Attendance record updated successfully!')
                return redirect('attendance_list')
            except Exception as e:
                messages.error(request, f'Error updating attendance record: {str(e)}')
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'attendance/form.html', {
        'form': form,
        'attendance': attendance,
        'title': 'Edit Attendance Record'
    })

@login_required
@transaction.atomic
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        try:
            attendance.delete()
            messages.success(request, 'Attendance record deleted successfully!')
            return redirect('attendance_list')
        except Exception as e:
            messages.error(request, f'Error deleting attendance record: {str(e)}')
            return redirect('attendance_detail', pk=pk)
    return render(request, 'attendance/delete.html', {'attendance': attendance})

@login_required
@transaction.atomic
def clock_in(request):
    # Check if the user already clocked in today without clocking out
    today_attendance = Attendance.objects.filter(
        user=request.user,
        clock_in__date=timezone.now().date(),
        clock_out__isnull=True
    ).first()
    
    if today_attendance:
        messages.warning(request, 'You have already clocked in today and have not clocked out yet!')
        return redirect('dashboard')
    
    try:
        # Create new attendance record
        attendance = Attendance.objects.create(
            user=request.user,
            clock_in=timezone.now()
        )
        
        # Get employee name if available
        employee_name = request.user.username
        if hasattr(request.user, 'employee'):
            employee_name = request.user.employee.names
        
        messages.success(request, f'Clock-in successful for {employee_name} at {attendance.clock_in.strftime("%H:%M:%S")}!')
    except Exception as e:
        messages.error(request, f'Error clocking in: {str(e)}')
    
    return redirect('dashboard')

@login_required
@transaction.atomic
def clock_out(request):
    # Find the last clock-in without clock-out
    attendance = Attendance.objects.filter(
        user=request.user,
        clock_out__isnull=True
    ).order_by('-clock_in').first()
    
    if not attendance:
        messages.warning(request, 'You have not clocked in yet!')
        return redirect('dashboard')
    
    try:
        # Update the attendance record
        attendance.clock_out = timezone.now()
        attendance.save()
        
        # Get employee name if available
        employee_name = request.user.username
        if hasattr(request.user, 'employee'):
            employee_name = request.user.employee.names
        
        # Calculate duration
        duration = attendance.duration
        
        messages.success(request, 
            f'Clock-out successful for {employee_name} at {attendance.clock_out.strftime("%H:%M:%S")}! '
            f'Duration: {duration}'
        )
    except Exception as e:
        messages.error(request, f'Error clocking out: {str(e)}')
    
    return redirect('dashboard')

@login_required
def register_attendance(request):
    if request.method == 'POST':
        document = request.POST.get('document')
        attendance_type = request.POST.get('attendance_type')
        description = request.POST.get('description', '')
        
        try:
            # Find employee by document
            employee = Employee.objects.get(document=document)
            user = employee.user
            current_time = timezone.now()
            current_date = current_time.date()
            
            # Handle attendance based on type
            if attendance_type == 'in':
                # Check if already clocked in
                existing_attendance = Attendance.objects.filter(
                    user=user,
                    clock_in__date=current_date,
                    clock_out__isnull=True
                ).first()
                
                if existing_attendance:
                    messages.warning(request, f'{employee.names} already clocked in today and has not clocked out yet!')
                else:
                    # Create new attendance record with clock_in
                    attendance = Attendance.objects.create(
                        user=user,
                        clock_in=current_time,
                        description=description
                    )
                    messages.success(request, f'Clock-in registered for {employee.names} at {attendance.clock_in.strftime("%H:%M:%S")}!')
            
            elif attendance_type == 'out':
                # Find the last clock-in without clock-out
                latest_attendance = Attendance.objects.filter(
                    user=user,
                    clock_out__isnull=True
                ).order_by('-clock_in').first()
                
                if not latest_attendance:
                    messages.warning(request, f'{employee.names} has not clocked in yet!')
                else:
                    # Verificar si el clock-in es del mismo día
                    if latest_attendance.clock_in.date() == current_date:
                        # Actualizar el registro existente
                        latest_attendance.clock_out = current_time
                        if description:
                            latest_attendance.description = description
                        latest_attendance.save()
                        
                        # Calculate duration
                        duration = latest_attendance.duration
                        
                        messages.success(request, 
                            f'Clock-out registered for {employee.names} at {latest_attendance.clock_out.strftime("%H:%M:%S")}! '
                            f'Duration: {duration}'
                        )
                    else:
                        # El último registro sin clock-out es de otro día, crear un nuevo registro
                        new_attendance = Attendance.objects.create(
                            user=user,
                            clock_out=current_time,
                            description=description or f'Auto-created: Missing clock-in from previous day {latest_attendance.clock_in.date()}'
                        )
                        
                        messages.warning(request, 
                            f'Created new clock-out record for {employee.names} at {new_attendance.clock_out.strftime("%H:%M:%S")}. '
                            f'The previous incomplete record from {latest_attendance.clock_in.date()} remains open.'
                        )
            
        except Employee.DoesNotExist:
            messages.error(request, f'No employee found with document: {document}')
        except Exception as e:
            messages.error(request, f'Error registering attendance: {str(e)}')
    
    return render(request, 'attendance/register.html')

@login_required
def verify_document(request):
    document = request.GET.get('document')
    if document:
        try:
            employee = Employee.objects.get(document=document)
            return JsonResponse({
                'valid': True,
                'employee_name': employee.names,
                'position': employee.position
            })
        except Employee.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'No employee found with this document'})
    return JsonResponse({'valid': False, 'message': 'Document is required'}) 