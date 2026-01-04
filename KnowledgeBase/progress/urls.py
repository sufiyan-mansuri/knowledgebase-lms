from django.urls import path
from .views import mark_lesson_as_complete

app_name = "progress"

urlpatterns = [
    path('<slug:slug>/module/<int:module_id>/lesson/<int:lesson_id>/complete', mark_lesson_as_complete, name='mark_lesson_as_complete'),
]
