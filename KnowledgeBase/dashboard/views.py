from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users

# Create your views here.
@allowed_users(['Students'])
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')

@allowed_users(['Instructors'])
def instructor_dashboard(request):
    return render(request, 'dashboard/instructor_dashboard.html')