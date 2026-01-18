from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course, Module
from lessons.models import Lesson
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db import IntegrityError
from core.mixins import InstructorRequiredMixin, NeverCacheMixin
from django.core.exceptions import PermissionDenied
from enrollments.models import Enrollment
from progress.models import LessonProgress
from users.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html' 

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.course_modules = Module.objects.filter(course=self.course).prefetch_related('lessons')

        if self.user.is_authenticated: 
            self.is_user_enrolled = Enrollment.objects.filter(
                course=self.course,
                student=self.user
            ).exists()
        else: 
            self.is_user_enrolled = False

        if self.is_user_enrolled:
            self.course_lessons = Lesson.objects.filter(module__course=self.course).count()            
            self.user_completed_lessons = LessonProgress.objects.filter(student=self.user, lesson__module__course=self.course, is_completed=True).count()

            user_lesson_progress = LessonProgress.objects.filter(
                student = self.user,
                lesson__module__course = self.course
            )

            self.user_progress_map = {progress.lesson.id: progress for progress in user_lesson_progress}

        return super().dispatch(request, *args, **kwargs) 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_modules"] = self.course_modules
        context['is_user_enrolled'] = self.is_user_enrolled 

        if self.is_user_enrolled:
            context['user_completed_lessons'] = self.user_completed_lessons
            context['course_progress'] = (self.user_completed_lessons/self.course_lessons)*100 
            context['user_progress_map'] = self.user_progress_map
            
            enrollment = Enrollment.objects.filter(
                course=self.course,
                student=self.user
            ).first()

            if enrollment.last_accessed_lesson:
                context['last_accessed_lesson'] = enrollment.last_accessed_lesson
            else: 
                first_lesson = Lesson.objects.filter(module__course=self.course).first()
                context['last_accessed_lesson'] = first_lesson

        return context

class CourseCreateView(LoginRequiredMixin, NeverCacheMixin, InstructorRequiredMixin, CreateView):
    model = Course
    extra_context = {'page_title': 'Create Course', 'button_info': 'Create Course'}
    fields = ['title', 'description', 'category', 'thumbnail', 'status']
    template_name = 'courses/course_form.html'

    def form_valid(self, form):
        course = form.save(commit=False)

        if not self.request.user.is_superuser:
            course.instructor = self.request.user
        
        return super().form_valid(form)
    
    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse('admin:courses_course_changelist')
        return reverse('instructor_dashboard')

class CourseUpdateView(LoginRequiredMixin, NeverCacheMixin, InstructorRequiredMixin, UpdateView):
    model = Course
    extra_context = {'page_title': 'Update Course', 'button_info': 'Update Course'}
    fields = ['title', 'description', 'category', 'thumbnail', 'status']

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Course.objects.all()

        return Course.objects.filter(instructor=user)

    def form_valid(self, form):
        course = form.save(commit=False)
        course.slug = slugify(course.title)
        return super().form_valid(form)

    template_name = 'courses/course_form.html'
    
    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse('admin:courses_course_changelist')
        return reverse('instructor_dashboard')

class CourseDeleteView(LoginRequiredMixin, NeverCacheMixin, InstructorRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Course.objects.all()

        return Course.objects.filter(instructor=user)
    
    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse('admin:courses_course_changelist')
        return reverse('instructor_dashboard')

class CourseModuleListView(LoginRequiredMixin, NeverCacheMixin, InstructorRequiredMixin, ListView):
    model = Module
    template_name = 'courses/module_list.html'

    def get_queryset(self):
        user = self.request.user
        self.course = Course.objects.get(slug=self.kwargs['slug'])

        if user.is_superuser or user == self.course.instructor:
            return Module.objects.filter(course=self.course)
        
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context

class ModuleCreateView(LoginRequiredMixin, NeverCacheMixin, InstructorRequiredMixin, CreateView):
    model = Module
    extra_context = {'page_title': 'Create Module', 'button_info': 'Create Module'}
    fields = ['title', 'order']
    template_name = 'courses/module_form.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        self.course = get_object_or_404(Course, slug=kwargs['slug'])

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        module = form.save(commit=False)
        module.course = self.course

        try:
            module.save()
        except IntegrityError:
            form.add_error('order', 'A module with this order already exists in this course.')
            return self.form_invalid(form)

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course 
        return context
    
    def get_success_url(self):
        return reverse_lazy('courses:module_list', kwargs={'slug': self.course.slug})
    
class ModuleUpdateView(LoginRequiredMixin, NeverCacheMixin, InstructorRequiredMixin, UpdateView):
    model = Module
    template_name = 'courses/module_form.html'
    extra_context = {'page_title': 'Update Module', 'button_info': 'Update Module'}
    fields = ['title', 'order']

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        course = self.course
        user = self.request.user

        if not (user.is_superuser or course.instructor == user):
            raise PermissionDenied

        return Module.objects.filter(course=self.course)    
    
    def form_valid(self, form):
        module = form.save(commit=False)
        module.course = self.course 

        try:
            module.save()
        except IntegrityError:
            form.add_error('order', 'A module with this order already exists in this course.')
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course 
        return context

    def get_success_url(self):
        return reverse_lazy('courses:module_list', kwargs={'slug': self.course.slug})

class ModuleDeleteView(LoginRequiredMixin, NeverCacheMixin, InstructorRequiredMixin, DeleteView):
    model = Module
    template_name = 'courses/module_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or self.course.instructor == user:
            return Module.objects.filter(course=self.course)

        raise PermissionDenied

    def get_success_url(self):
        return reverse_lazy('courses:module_list', kwargs={'slug': self.course.slug})