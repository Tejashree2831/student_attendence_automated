from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('export-excel/', views.export_attendance_excel, name='export_excel'),
]
