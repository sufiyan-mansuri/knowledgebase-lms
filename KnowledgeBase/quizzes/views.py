from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from .models import Quiz, Question, Option
from django.urls import reverse_lazy
from lessons.models import Lesson
from courses.models import Course, Module
from django.core.exceptions import ObjectDoesNotExist
from .forms import QuizAttemptForm
from progress.models import QuizAttempt, StudentAnswer
from enrollments.models import Enrollment
from core.mixins import InstructorRequiredMixin

# Create your views here.
class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'quizzes/quiz_detail.html'

    def get_object(self):
        lesson = get_object_or_404(
            Lesson,
            id=self.kwargs['lesson_id'],
            module__id=self.kwargs['module_id'],
            module__course__slug=self.kwargs['slug']
        )

        return lesson.quizzes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz_questions'] = self.object.questions.all()
        return context

class QuizCreateView(InstructorRequiredMixin, CreateView):
    model = Quiz
    fields = ['total_marks']
    extra_context = {'page_title': 'Create Quiz', 'button_info': 'Create Quiz'}
    template_name = 'quizzes/quiz_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(Lesson, id=kwargs['lesson_id'], module__id=kwargs['module_id'], module__course__slug=kwargs['slug'])

        if Quiz.objects.filter(lesson=self.lesson).exists():
            return redirect(
                'quizzes:quiz_detail',
                slug=self.lesson.module.course.slug,
                module_id=self.lesson.module.id,
                lesson_id=self.lesson.id
            )
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.lesson = self.lesson
        return super().form_valid(form) 

    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.lesson.module.course.slug,
            'module_id': self.lesson.module.id,
            'lesson_id': self.lesson.id,
        })

class QuizUpdateView(UpdateView):
    model = Quiz
    extra_context = {'page_title': 'Update Quiz', 'button_info': 'Update Quiz'}
    fields = ['total_marks']
    template_name = 'quizzes/quiz_form.html'

    def get_object(self):
        self.lesson = get_object_or_404(
            Lesson,
            id=self.kwargs['lesson_id'],
            module__id=self.kwargs['module_id'],
            module__course__slug=self.kwargs['slug']
        )

        return self.lesson.quizzes

    def get_success_url(self):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.lesson.module.course.slug,
            'module_id': self.lesson.module.id,
            'lesson_id': self.lesson.id,
        })

class QuizDeleteView(DeleteView):
    model = Quiz
    template_name = 'quizzes/quiz_confirm_delete.html'

    def get_object(self):
        self.lesson = get_object_or_404(
            Lesson,
            id=self.kwargs['lesson_id'],
            module__id=self.kwargs['module_id'],
            module__course__slug=self.kwargs['slug']
        )

        return self.lesson.quizzes
    
    def get_success_url(self, **kwargs):
        return reverse_lazy('lessons:lesson_list', kwargs={
            'slug': self.lesson.module.course.slug,
            'module_id': self.lesson.module.id
        })
    
class QuestionCreateView(CreateView):
    model = Question
    fields = ['question', 'marks', 'order']
    template_name = 'quizzes/question_form.html'
    extra_context = {'page_title': 'Create Question', 'button_info': 'Create Question'}

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(
            Quiz, 
            id=kwargs['quiz_id'],
            lesson__id=self.kwargs['lesson_id'],
            lesson__module__id=self.kwargs['module_id'],
            lesson__module__course__slug=self.kwargs['slug'],
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.quiz = self.quiz
        return super().form_valid(form) 
    
    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.quiz.lesson.module.course.slug,
            'module_id': self.quiz.lesson.module.id,
            'lesson_id': self.quiz.lesson.id,
        })
    
class QuestionUpdateView(UpdateView):
    model = Question
    fields = ['question', 'marks', 'order']
    template_name = 'quizzes/question_form.html'
    extra_context = {'page_title': 'Update Question', 'button_info': 'Update Question'}

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(
            Quiz, 
            id=kwargs['quiz_id'],
            lesson__id=self.kwargs['lesson_id'],
            lesson__module__id=self.kwargs['module_id'],
            lesson__module__course__slug=self.kwargs['slug'],
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Question.objects.filter(
            id=self.kwargs['pk'],
            quiz=self.quiz
        )

    def form_valid(self, form):
        form.instance.quiz = self.quiz
        return super().form_valid(form) 
    
    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.quiz.lesson.module.course.slug,
            'module_id': self.quiz.lesson.module.id,
            'lesson_id': self.quiz.lesson.id,
        })

class QuestionDeleteView(DeleteView):
    model = Question
    template_name = 'quizzes/question_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(
            Quiz, 
            id=kwargs['quiz_id'],
            lesson__id=self.kwargs['lesson_id'],
            lesson__module__id=self.kwargs['module_id'],
            lesson__module__course__slug=self.kwargs['slug'],
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Question.objects.filter(
            id=self.kwargs['pk'],
            quiz=self.quiz
        )

    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.quiz.lesson.module.course.slug,
            'module_id': self.quiz.lesson.module.id,
            'lesson_id': self.quiz.lesson.id,
        })
    
class QuestionDetailView(DetailView):
    model = Question
    template_name = 'quizzes/question_detail.html'

    def get_object(self):
        return get_object_or_404(
            Question,
            id=self.kwargs['question_id'],
            quiz__lesson__id=self.kwargs['lesson_id'],
            quiz__lesson__module__id=self.kwargs['module_id'],
            quiz__lesson__module__course__slug=self.kwargs['slug']
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_options'] = self.object.options.all()
        return context
    
class OptionCreateView(CreateView):
    model = Option
    fields = ['option', 'is_correct', 'order']
    template_name = 'quizzes/option_form.html'
    extra_context = {'page_title': 'Create Option', 'button_info': 'Create Option'}

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(
            Question, 
            id=kwargs['question_id'],
            quiz__id = self.kwargs['quiz_id'],
            quiz__lesson__id=self.kwargs['lesson_id'],
            quiz__lesson__module__id=self.kwargs['module_id'],
            quiz__lesson__module__course__slug=self.kwargs['slug'],
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.question = self.question
        return super().form_valid(form) 
    
    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:question_detail', kwargs={
            'slug': self.question.quiz.lesson.module.course.slug,
            'module_id': self.question.quiz.lesson.module.id,
            'lesson_id': self.question.quiz.lesson.id,
            'quiz_id': self.question.quiz.id,
            'question_id': self.question.id,
        })

class OptionUpdateView(UpdateView):
    model = Option
    fields = ['option', 'is_correct', 'order']
    template_name = 'quizzes/question_form.html'
    extra_context = {'page_title': 'Update Option', 'button_info': 'Update Option'}

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(
            Question, 
            id=kwargs['question_id'],
            quiz__id = self.kwargs['quiz_id'],
            quiz__lesson__id=self.kwargs['lesson_id'],
            quiz__lesson__module__id=self.kwargs['module_id'],
            quiz__lesson__module__course__slug=self.kwargs['slug'],
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Option.objects.filter(
            id=self.kwargs['pk'],
            question=self.question
        )

    def form_valid(self, form):
        form.instance.question = self.question
        return super().form_valid(form) 
    
    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:question_detail', kwargs={
            'slug': self.question.quiz.lesson.module.course.slug,
            'module_id': self.question.quiz.lesson.module.id,
            'lesson_id': self.question.quiz.lesson.id,
            'quiz_id': self.question.quiz.id,
            'question_id': self.question.id,
        })

class OptionDeleteView(DeleteView):
    model = Option
    template_name = 'quizzes/option_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(
            Question, 
            id=kwargs['question_id'],
            quiz__id = self.kwargs['quiz_id'],
            quiz__lesson__id=self.kwargs['lesson_id'],
            quiz__lesson__module__id=self.kwargs['module_id'],
            quiz__lesson__module__course__slug=self.kwargs['slug'],
        )
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Option.objects.filter(
            id=self.kwargs['pk'],
            question=self.question
        )

    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:question_detail', kwargs={
            'slug': self.question.quiz.lesson.module.course.slug,
            'module_id': self.question.quiz.lesson.module.id,
            'lesson_id': self.question.quiz.lesson.id,
            'quiz_id': self.question.quiz.id,
            'question_id': self.question.id,
        })

class QuizAttemptView(FormView):
    template_name = 'quizzes/quiz_attempt.html'
    form_class = QuizAttemptForm

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(
            Lesson,
            id=kwargs['lesson_id'],
            module__id=kwargs['module_id'],
            module__course__slug=kwargs['slug'],
        )

        self.quiz = self.lesson.quizzes
        self.course = self.lesson.module.course
        self.user = request.user

        if not Enrollment.objects.filter(course=self.course, student=self.user).exists():
            return redirect('courses:course_detail', slug=self.course.slug)
        
        if not self.course.status:
            return redirect('courses:course_detail', slug=self.course.slug)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        self.quiz = get_object_or_404(
            Quiz,
            lesson__id = self.kwargs['lesson_id']
        )

        kwargs['quiz'] = self.quiz
        return kwargs
    
    def form_valid(self, form):
        attempt = QuizAttempt.objects.create(
            student = self.request.user, 
            quiz = self.quiz,
        )

        score = 0

        for field, selected_option in form.cleaned_data.items():
            question_id = int(field.split('_')[1])
            question = Question.objects.get(id=question_id)

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
            )

            if selected_option.is_correct:
                score += 1
            
        attempt.score = score 
        attempt.save()

        return redirect('quizzes:quiz_result', self.quiz.lesson.module.course.slug, self.quiz.lesson.module.id, self.quiz.lesson.id, attempt.id)
    
class QuizResultView(DetailView):
    model = QuizAttempt
    template_name = 'quizzes/quiz_result.html'

class QuizOverviewPage(DetailView):
    model = Quiz
    template_name = 'quizzes/quiz_overview.html'