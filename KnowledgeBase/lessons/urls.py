from django.urls import path
from .views import ModuleLessonListView, LessonCreateView, LessonUpdateView, LessonDeleteView, LessonDetailView

app_name = 'lessons'

urlpatterns = [
    path('<slug:slug>/module/<int:module_id>/lessons', ModuleLessonListView.as_view(), name='lesson_list'),
    path('<slug:slug>/module/<int:module_id>/lessons/create', LessonCreateView.as_view(), name='lesson_create'),
    path('<slug:slug>/module/<int:module_id>/lessons/update/<int:pk>', LessonUpdateView.as_view(), name='lesson_update'),
    path('<slug:slug>/module/<int:module_id>/lessons/delete/<int:pk>', LessonDeleteView.as_view(), name='lesson_delete'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:pk>', LessonDetailView.as_view(), name='lesson_detail'),
]
