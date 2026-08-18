from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, FeePayment, Attendance, Mark


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
    paid_fees = FeePayment.objects.filter(status='Paid')
    total_fees = sum(payment.amount for payment in paid_fees)
    pending_fees = FeePayment.objects.filter(status='Pending').count()
    recent_payments = FeePayment.objects.all().order_by('-payment_date')[:5]
    
    context = {
        'total_students': total_students,
        'male_students': male_students,
        'female_students': female_students,
        'total_depts': total_depts,
        'total_fees': total_fees,
        'pending_fees': pending_fees,
        'recent_payments': recent_payments
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
        password = request.POST.get('password', '123456')
        profile_image = request.FILES.get('profile_image')
        
        # Simple validation
        if not all([roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address]):
            messages.error(request, "Error: All required fields must be filled.")
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
            address=address,
            password=password,
            profile_image=profile_image
        )
        messages.success(request, "Student Record Added Successfully!")
        return redirect('view_students')
        
    return render(request, 'add_student.html')

@login_required(login_url='login')
def view_students_view(request):
    students = Student.objects.all()
    return render(request, 'view_students.html', {'students': students})

@login_required(login_url='login')
def student_profile_view(request, id):
    student = get_object_or_404(Student, id=id)
    fee_payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    attendance = Attendance.objects.filter(student=student).order_by('-attendance_date')
    marks = Mark.objects.filter(student=student)
    return render(request, 'student_profile.html', {'student': student, 'fee_payments': fee_payments, 'attendance': attendance, 'marks': marks})

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

@login_required(login_url='login')
def add_fee_view(request):
    students = Student.objects.all()
    if request.method == 'POST':
        student_id = request.POST.get('student')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        if not all([student_id, amount, payment_date, payment_method, status]):
            messages.error(request, "Error: All fields are required.")
        else:
            FeePayment.objects.create(student_id=student_id, amount=amount, payment_date=payment_date, payment_method=payment_method, status=status)
            messages.success(request, "Fee Payment Added Successfully!")
            return redirect('view_fees')
    return render(request, 'add_fee.html', {'students': students})

@login_required(login_url='login')
def view_fees_view(request):
    fee_payments = FeePayment.objects.all().order_by('-payment_date')
    return render(request, 'view_fees.html', {'fee_payments': fee_payments})

@login_required(login_url='login')
def update_fee_view(request, id):
    fee_payment = get_object_or_404(FeePayment, id=id)
    students = Student.objects.all()
    if request.method == 'POST':
        fee_payment.student_id = request.POST.get('student')
        fee_payment.amount = request.POST.get('amount')
        fee_payment.payment_date = request.POST.get('payment_date')
        fee_payment.payment_method = request.POST.get('payment_method')
        fee_payment.status = request.POST.get('status')
        fee_payment.save()
        messages.success(request, "Fee Payment Updated Successfully!")
        return redirect('view_fees')
    return render(request, 'update_fee.html', {'fee_payment': fee_payment, 'students': students})

@login_required(login_url='login')
def delete_fee_view(request, id):
    fee_payment = get_object_or_404(FeePayment, id=id)
    fee_payment.delete()
    messages.success(request, "Fee Payment Deleted Successfully!")
    return redirect('view_fees')

@login_required(login_url='login')
def search_fee_view(request):
    query = request.GET.get('query', '').strip()
    fee_payments = FeePayment.objects.all().order_by('-payment_date')
    if query:
        fee_payments = fee_payments.filter(student__roll_number__icontains=query) | fee_payments.filter(student__first_name__icontains=query) | fee_payments.filter(student__last_name__icontains=query) | fee_payments.filter(status__icontains=query)
    return render(request, 'search_fee.html', {'fee_payments': fee_payments, 'query': query})

@login_required(login_url='login')
def fee_receipt_view(request, id):
    fee_payment = get_object_or_404(FeePayment, id=id)
    return render(request, 'fee_receipt.html', {'fee_payment': fee_payment})

@login_required(login_url='login')
def add_attendance_view(request):
    students = Student.objects.all()
    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date')
        if not attendance_date:
            messages.error(request, "Please select attendance date.")
        else:
            for student in students:
                status = request.POST.get('status_' + str(student.id))
                if status:
                    Attendance.objects.filter(student=student, attendance_date=attendance_date).delete()
                    Attendance.objects.create(student=student, attendance_date=attendance_date, status=status)
            messages.success(request, "Attendance Saved Successfully!")
            return redirect('view_attendance')
    return render(request, 'add_attendance.html', {'students': students})

@login_required(login_url='login')
def view_attendance_view(request):
    attendance_records = Attendance.objects.all().order_by('-attendance_date', 'student__first_name')
    students = Student.objects.all()
    attendance_summary = []
    for student in students:
        total_days = Attendance.objects.filter(student=student).count()
        present_days = Attendance.objects.filter(student=student, status='Present').count()
        percentage = 0
        if total_days > 0:
            percentage = round((present_days / total_days) * 100)
        attendance_summary.append({'student': student, 'total_days': total_days, 'present_days': present_days, 'percentage': percentage})
    return render(request, 'view_attendance.html', {'attendance_records': attendance_records, 'attendance_summary': attendance_summary})

@login_required(login_url='login')
def add_marks_view(request):
    students = Student.objects.all()
    if request.method == 'POST':
        Mark.objects.create(student_id=request.POST.get('student'), subject=request.POST.get('subject'), marks_obtained=request.POST.get('marks_obtained'), total_marks=request.POST.get('total_marks'))
        messages.success(request, "Marks Added Successfully!")
        return redirect('add_marks')
    return render(request, 'add_marks.html', {'students': students})

@login_required(login_url='login')
def departments_view(request):
    departments = Student.objects.values('department').distinct()
    return render(request, 'departments.html', {'departments': departments})

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

# ---------------- Student Views ---------------- #

def student_login_view(request):
    if 'student_id' in request.session:
        return redirect('student_dashboard')
    
    error_msg = None
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        password = request.POST.get('password')
        if not roll_number or not password:
            error_msg = "Please enter both Roll Number and Password."
        else:
            student = Student.objects.filter(roll_number=roll_number, password=password).first()
            if student:
                request.session['student_id'] = student.id
                return redirect('student_dashboard')
            else:
                error_msg = "Invalid Roll Number or Password!"
                
    return render(request, 'student_login.html', {'error_msg': error_msg})

def student_register_view(request):
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
        password = request.POST.get('password')
        profile_image = request.FILES.get('profile_image')
        
        if not all([roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password]):
            messages.error(request, "Error: All fields are required.")
            return render(request, 'student_register.html')
            
        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Error: Phone number must be exactly 10 numeric digits.")
            return render(request, 'student_register.html')
            
        if Student.objects.filter(roll_number=roll_number).exists():
            messages.error(request, f"Error: Student with Roll Number '{roll_number}' already exists.")
            return render(request, 'student_register.html')
            
        student = Student.objects.create(
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
            address=address,
            password=password,
            profile_image=profile_image
        )
        request.session['student_id'] = student.id
        messages.success(request, "Registration Successful! Welcome to your dashboard.")
        return redirect('student_dashboard')
        
    return render(request, 'student_register.html')

def student_dashboard_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')
        
    student = get_object_or_404(Student, id=student_id)
    attendance_records = Attendance.objects.filter(student=student).order_by('-attendance_date')
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='Present').count()
    absent_days = attendance_records.filter(status='Absent').count()
    attendance_percentage = round((present_days / total_days) * 100) if total_days > 0 else 0
    
    fee_payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    total_fees_paid = sum(p.amount for p in fee_payments if p.status == 'Paid')
    
    marks = Mark.objects.filter(student=student)
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': attendance_percentage,
        'fee_payments': fee_payments,
        'total_fees_paid': total_fees_paid,
        'marks': marks,
    }
    return render(request, 'student_dashboard.html', context)

def student_pay_fee_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')
        
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        
        if not amount or not payment_method:
            messages.error(request, "Please fill in all details.")
            return render(request, 'student_pay_fee.html', {'student': student})
            
        FeePayment.objects.create(
            student=student,
            amount=amount,
            payment_date=date.today(),
            payment_method=payment_method,
            status='Paid'
        )
        messages.success(request, "Fee Payment Completed Successfully!")
        return redirect('student_dashboard')
        
    return render(request, 'student_pay_fee.html', {'student': student})

def student_logout_view(request):
    if 'student_id' in request.session:
        del request.session['student_id']
    return redirect('student_login')

