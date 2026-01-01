from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course, Module
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db import IntegrityError

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        self.course_modules = Module.objects.filter(course=self.course)
        return super().dispatch(request, *args, **kwargs) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_modules"] = self.course_modules 
        return context


class CourseCreateView(CreateView):
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

class CourseUpdateView(UpdateView):
    model = Course
    extra_context = {'page_title': 'Update Course', 'button_info': 'Update Course'}
    fields = ['title', 'description', 'category', 'thumbnail', 'status']

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)

    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('instructor_dashboard')
        

class CourseDeleteView(DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('instructor_dashboard')

class CourseModuleListView(ListView):
    model = Module
    template_name = 'courses/module_list.html'

    def get_queryset(self):
        self.course = Course.objects.get(slug=self.kwargs['slug'])
        return Module.objects.filter(course=self.course)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context

class ModuleCreateView(CreateView):
    model = Module
    extra_context = {'page_title': 'Create Module', 'button_info': 'Create Module'}
    fields = ['title', 'order']
    template_name = 'courses/module_form.html'

    def dispatch(self, request, *args, **kwargs):
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
    
    def get_success_url(self):
        return reverse_lazy('courses:module_list', kwargs={'slug': self.course.slug})
    
class ModuleUpdateView(UpdateView):
    model = Module
    template_name = 'courses/module_form.html'
    extra_context = {'page_title': 'Create Module', 'button_info': 'Create Module'}
    fields = ['title', 'order']

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
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

class ModuleDeleteView(DeleteView):
    model = Module
    template_name = 'courses/module_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('courses:module_list', kwargs={'slug': self.course.slug})