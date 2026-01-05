from django.urls import path
from .views import QuizDetailView, QuizCreateView, QuizUpdateView, QuizDeleteView

app_name = "quizzes"

urlpatterns = [
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/create-quiz', QuizCreateView.as_view(), name='quiz_create'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz', QuizDetailView.as_view(), name='quiz_detail'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/update', QuizUpdateView.as_view(), name='quiz_update'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/delete', QuizDeleteView.as_view(), name='quiz_delete'),
]
