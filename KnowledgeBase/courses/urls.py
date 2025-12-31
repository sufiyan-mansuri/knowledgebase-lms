from django.urls import path
from courses.views import CourseListView, CourseDetailView, CourseCreateView, CourseUpdateView, CourseDeleteView

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    # path('', CourseDetailView.as_view(), name=''),
    path('<slug:slug>/update/', CourseUpdateView.as_view(), name='course_update'),
    path('<slug:slug>/delete/', CourseDeleteView.as_view(), name='course_delete'),
]
