from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('course-catalog/', views.course_catalog, name='course_catalog'),
]
