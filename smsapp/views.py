from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error_msg = None
    if request.method == 'POST':
        usernameInput = request.POST.get('username')
        passwordInput = request.POST.get('password')
        if not usernameInput or not passwordInput:
            error_msg = "Please enter both Username and Password."
        else:
            user = authenticate(request, username=usernameInput, password=passwordInput)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error_msg = "Invalid Username or Password!"
                
    return render(request, 'index.html', {'error_msg': error_msg})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    students = Student.objects.all()
    total_students = students.count()
    male_students = students.filter(gender='Male').count()
    female_students = students.filter(gender='Female').count()
    total_depts = students.values('department').distinct().count()
    
    context = {
        'total_students': total_students,
        'male_students': male_students,
        'female_students': female_students,
        'total_depts': total_depts
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def add_student_view(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        department = request.POST.get('department')
        year = request.POST.get('year')
        semester = request.POST.get('semester')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        # Simple validation
        if not all([roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address]):
            messages.error(request, "Error: All fields are required.")
            return render(request, 'add_student.html')
            
        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Error: Phone number must be exactly 10 numeric digits.")
            return render(request, 'add_student.html')
            
        if Student.objects.filter(roll_number=roll_number).exists():
            messages.error(request, f"Error: Student with Roll Number '{roll_number}' already exists.")
            return render(request, 'add_student.html')
            
        Student.objects.create(
            roll_number=roll_number,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            dob=dob,
            department=department,
            year=year,
            semester=semester,
            phone=phone,
            email=email,
            address=address
        )
        messages.success(request, "Student Record Added Successfully!")
        return redirect('view_students')
        
    return render(request, 'add_student.html')

@login_required(login_url='login')
def view_students_view(request):
    students = Student.objects.all()
    return render(request, 'view_students.html', {'students': students})

@login_required(login_url='login')
def update_student_view(request, id):
    student = get_object_or_404(Student, id=id)
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        department = request.POST.get('department')
        year = request.POST.get('year')
        semester = request.POST.get('semester')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        if not all([roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address]):
            messages.error(request, "Error: All fields are required.")
            return render(request, 'update_student.html', {'student': student})
            
        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Error: Phone number must be exactly 10 numeric digits.")
            return render(request, 'update_student.html', {'student': student})
            
        student.roll_number = roll_number
        student.first_name = first_name
        student.last_name = last_name
        student.gender = gender
        student.dob = dob
        student.department = department
        student.year = year
        student.semester = semester
        student.phone = phone
        student.email = email
        student.address = address
        student.save()
        
        messages.success(request, "Student Record Updated Successfully!")
        return redirect('view_students')
        
    return render(request, 'update_student.html', {'student': student})

@login_required(login_url='login')
def delete_student_view(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    messages.success(request, "Student Record Deleted Successfully!")
    return redirect('view_students')

@login_required(login_url='login')
def search_student_view(request):
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('search_type', 'name')
    students = Student.objects.all()
    
    if query:
        if search_type == 'roll':
            students = students.filter(roll_number__icontains=query)
        elif search_type == 'dept':
            students = students.filter(department__icontains=query)
        else:
            students = students.filter(first_name__icontains=query) | students.filter(last_name__icontains=query)
            
    return render(request, 'search_student.html', {'students': students, 'query': query, 'search_type': search_type})

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')
