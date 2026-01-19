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
from core.mixins import InstructorRequiredMixin, NeverCacheMixin
from core.mixins import StudentRequiredMixin, EnrollmentRequiredMixin, AttemptOwnershipMixin, CourseOwnerRequiredMixin, QuizEditableMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError

# Create your views here.
class QuizDetailView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    DetailView
    ):
    model = Quiz
    template_name = 'quizzes/quiz_detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

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

class QuizCreateView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin, 
    CourseOwnerRequiredMixin, 
    CreateView,
    ):

    model = Quiz
    fields = ['total_marks']
    extra_context = {'page_title': 'Create Quiz', 'button_info': 'Create Quiz'}
    template_name = 'quizzes/quiz_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.lesson = get_object_or_404(Lesson, id=kwargs['lesson_id'], module__id=kwargs['module_id'], module__course__slug=kwargs['slug'])
        self.course = self.lesson.module.course

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course 
        context["lesson"] = self.lesson
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.lesson.module.course.slug,
            'module_id': self.lesson.module.id,
            'lesson_id': self.lesson.id,
        })

class QuizUpdateView(
    LoginRequiredMixin, 
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    QuizEditableMixin,
    UpdateView,
    ):
    model = Quiz
    extra_context = {'page_title': 'Update Quiz', 'button_info': 'Update Quiz'}
    fields = ['total_marks', 'status']
    template_name = 'quizzes/quiz_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.quiz = self.get_object()

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        self.lesson = get_object_or_404(
            Lesson,
            id=self.kwargs['lesson_id'],
            module__id=self.kwargs['module_id'],
            module__course__slug=self.kwargs['slug']
        )

        return self.lesson.quizzes

    def form_valid(self, form):
        quiz = form.instance

        if quiz.status == 'locked':
            form.add_error(None, 'This quiz is locked and cannot be modified.')
            return self.form_invalid(form)
        
        if quiz.status == 'active':
            questions = self.object.questions.all()
            total = sum(question.marks for question in questions)

            for question in questions:
                if not question.is_valid_question():
                    form.add_error(
                        None,
                        'Each question must have at least 2 options and exactly 1 correct option.'
                    )

            if total != quiz.total_marks:
                form.add_error('status', 'Total marks of questions must exactly match quiz total marks.')
                return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course 
        context["lesson"] = self.lesson
        return context

    def get_success_url(self):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.lesson.module.course.slug,
            'module_id': self.lesson.module.id,
            'lesson_id': self.lesson.id,
        })

class QuizDeleteView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    QuizEditableMixin,
    DeleteView
    ):
    model = Quiz
    template_name = 'quizzes/quiz_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.quiz = self.get_object()

        return super().dispatch(request, *args, **kwargs)

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
    
class QuestionCreateView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    QuizEditableMixin,
    CreateView
    ):
    model = Question
    fields = ['question', 'marks', 'order']
    template_name = 'quizzes/question_form.html'
    extra_context = {'page_title': 'Create Question', 'button_info': 'Create Question'}

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
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

        try:
            form.save()
        except IntegrityError:
            form.add_error('order', 'A question with this order already exists in this quiz.')
            return self.form_invalid(form)

        return super().form_valid(form) 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        context["quiz"] = self.quiz
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.quiz.lesson.module.course.slug,
            'module_id': self.quiz.lesson.module.id,
            'lesson_id': self.quiz.lesson.id,
        })
    
class QuestionUpdateView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    QuizEditableMixin,
    UpdateView
    ):
    model = Question
    fields = ['question', 'marks', 'order']
    template_name = 'quizzes/question_form.html'
    extra_context = {'page_title': 'Update Question', 'button_info': 'Update Question'}

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
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

        try:
            form.save()
        except IntegrityError:
            form.add_error('order', 'A question with this order already exists in this quiz.')
            return self.form_invalid(form)

        return super().form_valid(form) 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        context["quiz"] = self.quiz
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:quiz_detail', kwargs={
            'slug': self.quiz.lesson.module.course.slug,
            'module_id': self.quiz.lesson.module.id,
            'lesson_id': self.quiz.lesson.id,
        })

class QuestionDeleteView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    QuizEditableMixin,
    DeleteView
    ):
    model = Question
    template_name = 'quizzes/question_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
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
    
class QuestionDetailView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    DetailView
    ):
    model = Question
    template_name = 'quizzes/question_detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.quiz = get_object_or_404(Quiz, id=kwargs['quiz_id'])

        return super().dispatch(request, *args, **kwargs)

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
    
class OptionCreateView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    QuizEditableMixin,
    CreateView
    ):
    model = Option
    fields = ['option', 'is_correct', 'order']
    template_name = 'quizzes/option_form.html'
    extra_context = {'page_title': 'Create Option', 'button_info': 'Create Option'}

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.quiz = get_object_or_404(Quiz, id=kwargs['quiz_id'])

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

        correct_option_exists = Option.objects.filter(
            question=self.question,
            is_correct=True
        ).exists()

        if correct_option_exists and form.cleaned_data.get('is_correct'):
            form.add_error(
                'is_correct',
                'This question already has a correct option.'
            )
            return self.form_invalid(form)

        try: 
            form.save()
        except IntegrityError:
            form.add_error('order', 'An opiton with this order already exists in this question.')
            return self.form_invalid(form)

        return super().form_valid(form) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        context["quiz"] = self.quiz
        context["question"] = self.question
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('quizzes:question_detail', kwargs={
            'slug': self.question.quiz.lesson.module.course.slug,
            'module_id': self.question.quiz.lesson.module.id,
            'lesson_id': self.question.quiz.lesson.id,
            'quiz_id': self.question.quiz.id,
            'question_id': self.question.id,
        })

class OptionUpdateView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    QuizEditableMixin,
    UpdateView
):
    model = Option
    fields = ['option', 'is_correct', 'order']
    template_name = 'quizzes/option_form.html'
    extra_context = {
        'page_title': 'Update Option',
        'button_info': 'Update Option'
    }

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.quiz = get_object_or_404(Quiz, id=kwargs['quiz_id'])

        self.question = get_object_or_404(
            Question,
            id=kwargs['question_id'],
            quiz__id=kwargs['quiz_id'],
            quiz__lesson__id=kwargs['lesson_id'],
            quiz__lesson__module__id=kwargs['module_id'],
            quiz__lesson__module__course__slug=kwargs['slug'],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Option.objects.filter(question=self.question)

    def form_valid(self, form):
        option = form.save(commit=False)
        option.question = self.question

        if option.is_correct:
            correct_option_exists = Option.objects.filter(
                question=self.question,
                is_correct=True
            ).exclude(id=option.id).exists()

            if correct_option_exists:
                form.add_error(
                    'is_correct',
                    'This question already has a correct option.'
                )
                return self.form_invalid(form)

        try:
            option.save()
        except IntegrityError:
            form.add_error(
                'order',
                'An option with this order already exists for this question.'
            )
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['quiz'] = self.quiz
        context['question'] = self.question
        return context

    def get_success_url(self):
        return reverse_lazy(
            'quizzes:question_detail',
            kwargs={
                'slug': self.question.quiz.lesson.module.course.slug,
                'module_id': self.question.quiz.lesson.module.id,
                'lesson_id': self.question.quiz.lesson.id,
                'quiz_id': self.question.quiz.id,
                'question_id': self.question.id,
            }
        )

class OptionDeleteView(
    LoginRequiredMixin,
    NeverCacheMixin,
    InstructorRequiredMixin,
    CourseOwnerRequiredMixin,
    QuizEditableMixin,
    DeleteView
    ):
    model = Option
    template_name = 'quizzes/option_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.quiz = get_object_or_404(Quiz, id=kwargs['quiz_id'])

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

class QuizAttemptView(LoginRequiredMixin, NeverCacheMixin, StudentRequiredMixin, EnrollmentRequiredMixin, FormView):
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

        if self.quiz.status not in ['active', 'locked']:
            raise PermissionDenied

        if self.user.is_authenticated:
            quiz_attempt = QuizAttempt.objects.filter(student=self.user, quiz=self.quiz).first()
        else:
            quiz_attempt = None

        if quiz_attempt:
            return redirect('quizzes:quiz_result', self.quiz.lesson.module.course.slug, self.quiz.lesson.module.id, self.quiz.lesson.id, quiz_attempt.id)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        self.quiz = get_object_or_404(
            Quiz,
            lesson__id = self.kwargs['lesson_id']
        )

        kwargs['quiz'] = self.quiz
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.quiz
        return context

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
                score += question.marks
            
        attempt.score = score 
        attempt.save()

        if self.quiz.status == 'active':
            self.quiz.status = 'locked'
            self.quiz.save()

        return redirect('quizzes:quiz_result', self.quiz.lesson.module.course.slug, self.quiz.lesson.module.id, self.quiz.lesson.id, attempt.id)
    
class QuizResultView(LoginRequiredMixin, NeverCacheMixin, StudentRequiredMixin, AttemptOwnershipMixin, DetailView):
    model = QuizAttempt
    template_name = 'quizzes/quiz_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, slug=self.kwargs['slug'])
        context["quiz"] = get_object_or_404(Quiz, lesson=self.kwargs['lesson_id'])
        context["total_questions"] = Question.objects.filter(quiz=context['quiz']).count()
        context["correct_questions"] = StudentAnswer.objects.filter(attempt=self.object, selected_option__is_correct=True).count()
        context["incorrect_questions"] = StudentAnswer.objects.filter(attempt=self.object, selected_option__is_correct=False).count()
        return context 

class QuizOverviewPage(LoginRequiredMixin, NeverCacheMixin, StudentRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quizzes/quiz_overview.html'

    
    