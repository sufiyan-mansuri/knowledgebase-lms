from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Quiz, Question, Option
from django.urls import reverse_lazy
from lessons.models import Lesson
from courses.models import Course, Module
from django.core.exceptions import ObjectDoesNotExist

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

class QuizCreateView(CreateView):
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