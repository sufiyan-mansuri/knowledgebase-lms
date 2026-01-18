from django.urls import path
from courses.views import CourseDetailView, CourseCreateView, CourseUpdateView, CourseDeleteView, CourseModuleListView, ModuleCreateView, ModuleUpdateView, ModuleDeleteView

app_name = 'courses'

urlpatterns = [
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    path('<slug:slug>/update/', CourseUpdateView.as_view(), name='course_update'),
    path('<slug:slug>/delete/', CourseDeleteView.as_view(), name='course_delete'),
    path('<slug:slug>/modules/', CourseModuleListView.as_view(), name='module_list'),
    path('<slug:slug>/create-module/', ModuleCreateView.as_view(), name='module_create'),
    path('<slug:slug>/update-module/<int:pk>', ModuleUpdateView.as_view(), name='module_update'),
    path('<slug:slug>/delete-module/<int:pk>', ModuleDeleteView.as_view(), name='module_delete'),
]
