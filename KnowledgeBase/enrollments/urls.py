from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('<slug:slug>/enroll', views.enroll, name='enroll'),
]
