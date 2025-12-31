from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course
from django.urls import reverse_lazy
from django.utils.text import slugify

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    pass

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
