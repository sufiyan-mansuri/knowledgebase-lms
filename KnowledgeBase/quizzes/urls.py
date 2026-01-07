from django.urls import path
from .views import QuizDetailView, QuizCreateView, QuizUpdateView, QuizDeleteView, QuestionCreateView, QuestionUpdateView, QuestionDeleteView, QuestionDetailView, OptionCreateView, OptionUpdateView, OptionDeleteView, QuizAttemptView, QuizResultView, QuizOverviewPage

app_name = "quizzes"

urlpatterns = [
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/create-quiz', QuizCreateView.as_view(), name='quiz_create'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz', QuizDetailView.as_view(), name='quiz_detail'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/update', QuizUpdateView.as_view(), name='quiz_update'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/delete', QuizDeleteView.as_view(), name='quiz_delete'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/<int:pk>/overview', QuizOverviewPage.as_view(), name='quiz_overview'),

    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/<int:quiz_id>/questions/create', QuestionCreateView.as_view(), name='question_create'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/<int:quiz_id>/questions/<int:pk>/update', QuestionUpdateView.as_view(), name='question_update'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/<int:quiz_id>/questions/<int:pk>/delete', QuestionDeleteView.as_view(), name='question_delete'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/<int:quiz_id>/questions/<int:question_id>', QuestionDetailView.as_view(), name='question_detail'),
    
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/<int:quiz_id>/questions/<int:question_id>/options/create', OptionCreateView.as_view(), name='option_create'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/<int:quiz_id>/questions/<int:question_id>/options/<int:pk>/update', OptionUpdateView.as_view(), name='option_update'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/<int:quiz_id>/questions/<int:question_id>/options/<int:pk>/delete', OptionDeleteView.as_view(), name='option_delete'),

    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/attempt/', QuizAttemptView.as_view(), name='quiz_attempt'),
    path('<slug:slug>/module/<int:module_id>/lessons/<int:lesson_id>/quiz/result/<int:pk>', QuizResultView.as_view(), name='quiz_result')
]