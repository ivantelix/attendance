from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('<int:pk>/', views.attendance_detail, name='attendance_detail'),
    path('<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
    path('<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    path('register-attendance/', views.register_attendance, name='register_attendance'),
    path('verify-document/', views.verify_document, name='verify_document'),
] 