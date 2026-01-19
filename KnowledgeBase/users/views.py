from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages

# Create your views here.
def assign_group(user):
    user.groups.clear()

    if user.role == 'instructor':
        group, _ = Group.objects.get_or_create(name='Instructors')
    else:
        group, _ = Group.objects.get_or_create(name='Students')
    
    user.groups.add(group)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                assign_group(user)
                
            messages.info(request, 'Account created. Please log in.')
            return redirect('login')
    else:
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Students').exists():
                return redirect('student_dashboard')
            
            if request.user.groups.filter(name='Instructor').exists():
                return redirect('instructor_dashboard')
            
            if request.user.is_superuser:
                return redirect('/admin/')

        form = CustomUserCreationForm() 

    return render(request, 'users/register.html', {'form': form})
        
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.groups.filter(name='Students').exists():
                return redirect('student_dashboard')

            if user.groups.filter(name='Instructors').exists():
                return redirect('instructor_dashboard')
            
            if user.is_superuser:
                return redirect('/admin/')

            return redirect('home')
    else:
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Students').exists():
                return redirect('student_dashboard')
            
            if request.user.groups.filter(name='Instructors').exists():
                return redirect('instructor_dashboard')
            
            if request.user.is_superuser:
                return redirect('/admin/')

        form = AuthenticationForm(request) 

    return render(request, 'users/login.html', {'form': form})

@never_cache
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

