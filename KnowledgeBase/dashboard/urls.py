from django.urls import path
from . import views

urlpatterns = [
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor_dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
]
