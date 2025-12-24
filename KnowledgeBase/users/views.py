from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.db import transaction


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
                
            return redirect('login')
    else:
        form = CustomUserCreationForm() 

    return render(request, 'users/register.html', {'form': form})
        
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == 'instructor':
                return redirect('instructor_dashboard')
            
            return redirect('student_dashboard')
    else:
        form = AuthenticationForm(request) 

    return render(request, 'users/login.html', {'form': form})

def dashboard(request):
    return render(request, 'users/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

