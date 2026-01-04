from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course, Module
from lessons.models import Lesson
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db import IntegrityError
from core.mixins import InstructorRequiredMixin
from django.core.exceptions import PermissionDenied
from enrollments.models import Enrollment

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html' 

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.course_modules = Module.objects.filter(course=self.course).prefetch_related('lessons')

        self.is_user_enrolled = Enrollment.objects.filter(
            course=self.course,
            student=self.user
        ).exists()

        return super().dispatch(request, *args, **kwargs) 
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_modules"] = self.course_modules
        context['is_user_enrolled'] = self.is_user_enrolled 
        return context

class CourseCreateView(InstructorRequiredMixin, CreateView):
    model = Course
    extra_context = {'page_title': 'Create Course', 'button_info': 'Create Course'}
    fields = ['title', 'description', 'category', 'thumbnail', 'status']
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('instructor_dashboard')

    def form_valid(self, form):
        course = form.save(commit=False)
        course.instructor = self.request.user
        course.save()
        return super().form_valid(form)

class CourseUpdateView(InstructorRequiredMixin, UpdateView):
    model = Course
    extra_context = {'page_title': 'Update Course', 'button_info': 'Update Course'}
    fields = ['title', 'description', 'category', 'thumbnail', 'status']

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Course.objects.all()

        return Course.objects.filter(instructor=user)

    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('instructor_dashboard')
        

class CourseDeleteView(InstructorRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('instructor_dashboard')

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Course.objects.all()

        return Course.objects.filter(instructor=user)

class CourseModuleListView(InstructorRequiredMixin, ListView):
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

class ModuleCreateView(InstructorRequiredMixin, CreateView):
    model = Module
    extra_context = {'page_title': 'Create Module', 'button_info': 'Create Module'}
    fields = ['title', 'order']
    template_name = 'courses/module_form.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        self.course = get_object_or_404(Course, slug=kwargs['slug'])

        if not (user.is_superuser or self.course.instructor == user):
            raise PermissionDenied

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
    
    def get_success_url(self):
        return reverse_lazy('courses:module_list', kwargs={'slug': self.course.slug})
    
class ModuleUpdateView(InstructorRequiredMixin, UpdateView):
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

    def get_success_url(self):
        return reverse_lazy('courses:module_list', kwargs={'slug': self.course.slug})

class ModuleDeleteView(InstructorRequiredMixin, DeleteView):
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