from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/enroll', views.enroll, name='enroll'),
]
