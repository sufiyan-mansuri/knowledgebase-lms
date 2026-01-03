from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Lesson
from courses.models import Module, Course
from django.urls import reverse_lazy
from django.db import IntegrityError
from core.mixins import InstructorRequiredMixin
from django.core.exceptions import PermissionDenied

# Create your views here. 
class ModuleLessonListView(InstructorRequiredMixin, ListView):
    model = Lesson
    template_name = 'lessons/lesson_list.html'
    
    def get_queryset(self):
        self.course = Course.objects.get(slug=self.kwargs['slug'])
        self.module = Module.objects.get(id=self.kwargs['module_id'])
        user = self.request.user

        if not (user.is_superuser or self.course.instructor == user):
            raise PermissionDenied

        return Lesson.objects.filter(module=self.module)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        context["module"] = self.module
        return context

class LessonCreateView(InstructorRequiredMixin, CreateView):
    model = Lesson
    extra_context = {'page_title': 'Create Lesson', 'button_info': 'Create Lesson'}
    fields = ['title', 'content', 'video_url', 'order']
    template_name = 'lessons/lesson_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.module = get_object_or_404(Module, id=kwargs['module_id'])
        user = self.request.user

        if not (user.is_superuser or self.course.instructor == user):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        lesson = form.save(commit=False)
        lesson.module = self.module

        try:
            lesson.save()
        except IntegrityError:
            form.add_error('order', 'A lesson with this order already exists in this module.')
            return self.form_invalid(form)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lessons:lesson_list', kwargs={'slug': self.course.slug, 'module_id': self.module.id})

class LessonUpdateView(InstructorRequiredMixin, UpdateView):
    model = Lesson
    template_name = 'lessons/lesson_form.html'
    extra_context = {'page_title': 'Update Lesson', 'button_info': 'Update Lesson'}
    fields = ['title', 'content', 'video_url', 'order']

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.module = get_object_or_404(Module, id=kwargs['module_id'])

        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        user = self.request.user

        if not (user.is_superuser or self.course.instructor == user):
            raise PermissionDenied
        
        return Lesson.objects.filter(module=self.module)
    
    def form_valid(self, form):
        lesson = form.save(commit=False)
        lesson.module = self.module 

        try:
            lesson.save()
        except IntegrityError:
            form.add_error('order', 'A lesson with this order already exists in this module.')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('lessons:lesson_list', kwargs={'slug': self.course.slug, 'module_id': self.module.id})

class LessonDeleteView(DeleteView):
    model = Lesson
    template_name = 'lessons/lesson_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.module = get_object_or_404(Module, id=kwargs['module_id'])

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or self.course.instructor == user:
            return Lesson.objects.filter(module=self.module)

        raise PermissionDenied

    def get_success_url(self):
        return reverse_lazy('lessons:lesson_list', kwargs={'slug': self.course.slug, 'module_id': self.module.id})
    
class LessonDetailView(DetailView):
    model = Lesson 
    template_name = 'lessons/lesson_detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.module = get_object_or_404(Module, id=kwargs['module_id'], course=self.course)

        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Lesson.objects.filter(module=self.module)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        
        context["course"] = self.course
        context["module"] = self.module
        context["previous_lesson"] = (
            Lesson.objects
            .filter(module=self.module, order__lt = lesson.order)
            .order_by('-order')
            .first()
        )
        context["next_lesson"] = (
            Lesson.objects
            .filter(module=self.module, order__gt = lesson.order)
            .order_by('order')
            .first()
        )

        return context
    

    

    