"""
views.py — Student Management System
Database operations: PyMySQL + raw SQL queries (no Django ORM)
Django is used only for: URL routing, views, templates, sessions, auth, messages
"""

from datetime import date

import pymysql

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .db import get_connection, R


# ================================================================
# Helper — fetch all rows as list of R objects
# ================================================================

def _fetch_all(cursor):
    """Return all rows from cursor as a list of R objects."""
    return [R(row) for row in cursor.fetchall()]


def _fetch_one(cursor):
    """Return one row as an R object, or None."""
    row = cursor.fetchone()
    return R(row) if row else None


# ================================================================
# ADMIN AUTH VIEWS
# ================================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_msg = None
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        if not username_input or not password_input:
            error_msg = "Please enter both Username and Password."
        else:
            user = authenticate(request, username=username_input, password=password_input)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error_msg = "Invalid Username or Password!"

    return render(request, 'index.html', {'error_msg': error_msg})


def logout_view(request):
    logout(request)
    return redirect('login')


# ================================================================
# DASHBOARD
# ================================================================

@login_required(login_url='login')
def dashboard_view(request):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Total students
            cur.execute("SELECT COUNT(*) AS cnt FROM smsapp_student")
            total_students = cur.fetchone()['cnt']

            # Male / Female count
            cur.execute("SELECT COUNT(*) AS cnt FROM smsapp_student WHERE gender = 'Male'")
            male_students = cur.fetchone()['cnt']

            cur.execute("SELECT COUNT(*) AS cnt FROM smsapp_student WHERE gender = 'Female'")
            female_students = cur.fetchone()['cnt']

            # Distinct departments
            cur.execute("SELECT COUNT(DISTINCT department) AS cnt FROM smsapp_student")
            total_depts = cur.fetchone()['cnt']

            # Total paid fees (SUM)
            cur.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM smsapp_feepayment WHERE status = 'Paid'")
            total_fees = cur.fetchone()['total']

            # Pending fee count
            cur.execute("SELECT COUNT(*) AS cnt FROM smsapp_feepayment WHERE status = 'Pending'")
            pending_fees = cur.fetchone()['cnt']

            # Recent 5 payments with student name via JOIN
            cur.execute("""
                SELECT fp.id, fp.amount, fp.payment_date, fp.payment_method, fp.status,
                       s.id AS student_id, s.first_name, s.last_name, s.roll_number
                FROM smsapp_feepayment fp
                JOIN smsapp_student s ON fp.student_id = s.id
                ORDER BY fp.payment_date DESC
                LIMIT 5
            """)
            rows = cur.fetchall()
            recent_payments = []
            for row in rows:
                payment = R({
                    'id': row['id'],
                    'amount': row['amount'],
                    'payment_date': row['payment_date'],
                    'payment_method': row['payment_method'],
                    'status': row['status'],
                    'student': {
                        'id': row['student_id'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'roll_number': row['roll_number'],
                    }
                })
                recent_payments.append(payment)

    finally:
        conn.close()

    context = {
        'total_students': total_students,
        'male_students': male_students,
        'female_students': female_students,
        'total_depts': total_depts,
        'total_fees': total_fees,
        'pending_fees': pending_fees,
        'recent_payments': recent_payments,
    }
    return render(request, 'dashboard.html', context)


# ================================================================
# STUDENT CRUD
# ================================================================

@login_required(login_url='login')
def add_student_view(request):
    if request.method == 'POST':
        roll_number  = request.POST.get('roll_number', '').strip()
        first_name   = request.POST.get('first_name', '').strip()
        last_name    = request.POST.get('last_name', '').strip()
        gender       = request.POST.get('gender', '').strip()
        dob          = request.POST.get('dob', '').strip()
        department   = request.POST.get('department', '').strip()
        year         = request.POST.get('year', '').strip()
        semester     = request.POST.get('semester', '').strip()
        phone        = request.POST.get('phone', '').strip()
        email        = request.POST.get('email', '').strip()
        address      = request.POST.get('address', '').strip()
        password     = request.POST.get('password', '123456').strip()
        profile_image = request.FILES.get('profile_image')

        # Validation
        if not all([roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address]):
            messages.error(request, "Error: All required fields must be filled.")
            return render(request, 'add_student.html')

        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Error: Phone number must be exactly 10 numeric digits.")
            return render(request, 'add_student.html')

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Check duplicate roll number
                cur.execute("SELECT id FROM smsapp_student WHERE roll_number = %s", (roll_number,))
                if cur.fetchone():
                    messages.error(request, f"Error: Student with Roll Number '{roll_number}' already exists.")
                    return render(request, 'add_student.html')

                # Save profile image path if uploaded
                image_name = None
                if profile_image:
                    import os
                    from django.conf import settings
                    upload_dir = settings.MEDIA_ROOT / 'student_images'
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    image_name = 'student_images/' + profile_image.name
                    with open(settings.MEDIA_ROOT / image_name, 'wb') as f:
                        for chunk in profile_image.chunks():
                            f.write(chunk)

                # INSERT student
                cur.execute("""
                    INSERT INTO smsapp_student
                        (roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password, profile_image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password, image_name))
                conn.commit()

        finally:
            conn.close()

        messages.success(request, "Student Record Added Successfully!")
        return redirect('view_students')

    return render(request, 'add_student.html')


@login_required(login_url='login')
def view_students_view(request):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM smsapp_student ORDER BY id")
            students = _fetch_all(cur)
    finally:
        conn.close()
    return render(request, 'view_students.html', {'students': students})


@login_required(login_url='login')
def student_profile_view(request, id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM smsapp_student WHERE id = %s", (id,))
            student = _fetch_one(cur)
            if not student:
                messages.error(request, "Student not found.")
                return redirect('view_students')

            # Fee payments with student info (JOIN for completeness)
            cur.execute("""
                SELECT fp.*, s.first_name, s.last_name, s.roll_number
                FROM smsapp_feepayment fp
                JOIN smsapp_student s ON fp.student_id = s.id
                WHERE fp.student_id = %s
                ORDER BY fp.payment_date DESC
            """, (id,))
            fee_rows = cur.fetchall()
            fee_payments = []
            for row in fee_rows:
                fee_payments.append(R({
                    'id': row['id'],
                    'amount': row['amount'],
                    'payment_date': row['payment_date'],
                    'payment_method': row['payment_method'],
                    'status': row['status'],
                    'student': {
                        'id': id,
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'roll_number': row['roll_number'],
                    }
                }))

            # Attendance records
            cur.execute("""
                SELECT att.*, s.first_name, s.last_name, s.roll_number
                FROM smsapp_attendance att
                JOIN smsapp_student s ON att.student_id = s.id
                WHERE att.student_id = %s
                ORDER BY att.attendance_date DESC
            """, (id,))
            att_rows = cur.fetchall()
            attendance = []
            for row in att_rows:
                attendance.append(R({
                    'id': row['id'],
                    'attendance_date': row['attendance_date'],
                    'status': row['status'],
                    'student': {
                        'id': id,
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'roll_number': row['roll_number'],
                    }
                }))

            # Marks
            cur.execute("""
                SELECT m.*, s.first_name, s.last_name
                FROM smsapp_mark m
                JOIN smsapp_student s ON m.student_id = s.id
                WHERE m.student_id = %s
            """, (id,))
            marks = _fetch_all(cur)

    finally:
        conn.close()

    return render(request, 'student_profile.html', {
        'student': student,
        'fee_payments': fee_payments,
        'attendance': attendance,
        'marks': marks,
    })


@login_required(login_url='login')
def update_student_view(request, id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM smsapp_student WHERE id = %s", (id,))
            student = _fetch_one(cur)
            if not student:
                messages.error(request, "Student not found.")
                return redirect('view_students')

        if request.method == 'POST':
            roll_number = request.POST.get('roll_number', '').strip()
            first_name  = request.POST.get('first_name', '').strip()
            last_name   = request.POST.get('last_name', '').strip()
            gender      = request.POST.get('gender', '').strip()
            dob         = request.POST.get('dob', '').strip()
            department  = request.POST.get('department', '').strip()
            year        = request.POST.get('year', '').strip()
            semester    = request.POST.get('semester', '').strip()
            phone       = request.POST.get('phone', '').strip()
            email       = request.POST.get('email', '').strip()
            address     = request.POST.get('address', '').strip()

            if not all([roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address]):
                messages.error(request, "Error: All fields are required.")
                return render(request, 'update_student.html', {'student': student})

            if len(phone) != 10 or not phone.isdigit():
                messages.error(request, "Error: Phone number must be exactly 10 numeric digits.")
                return render(request, 'update_student.html', {'student': student})

            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE smsapp_student
                    SET roll_number = %s, first_name = %s, last_name = %s, gender = %s,
                        dob = %s, department = %s, year = %s, semester = %s,
                        phone = %s, email = %s, address = %s
                    WHERE id = %s
                """, (roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, id))
                conn.commit()

            messages.success(request, "Student Record Updated Successfully!")
            return redirect('view_students')
    finally:
        conn.close()

    return render(request, 'update_student.html', {'student': student})


@login_required(login_url='login')
def delete_student_view(request, id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM smsapp_student WHERE id = %s", (id,))
            conn.commit()
    finally:
        conn.close()
    messages.success(request, "Student Record Deleted Successfully!")
    return redirect('view_students')


@login_required(login_url='login')
def search_student_view(request):
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('search_type', 'name')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if query:
                if search_type == 'roll':
                    cur.execute(
                        "SELECT * FROM smsapp_student WHERE roll_number LIKE %s ORDER BY id",
                        (f'%{query}%',)
                    )
                elif search_type == 'dept':
                    cur.execute(
                        "SELECT * FROM smsapp_student WHERE department LIKE %s ORDER BY id",
                        (f'%{query}%',)
                    )
                else:
                    cur.execute(
                        "SELECT * FROM smsapp_student WHERE first_name LIKE %s OR last_name LIKE %s ORDER BY id",
                        (f'%{query}%', f'%{query}%')
                    )
            else:
                cur.execute("SELECT * FROM smsapp_student ORDER BY id")

            students = _fetch_all(cur)
    finally:
        conn.close()

    return render(request, 'search_student.html', {
        'students': students,
        'query': query,
        'search_type': search_type,
    })


# ================================================================
# FEES
# ================================================================

@login_required(login_url='login')
def add_fee_view(request):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM smsapp_student ORDER BY first_name, last_name")
            students = _fetch_all(cur)

        if request.method == 'POST':
            student_id     = request.POST.get('student')
            amount         = request.POST.get('amount')
            payment_date   = request.POST.get('payment_date')
            payment_method = request.POST.get('payment_method')
            status         = request.POST.get('status')

            if not all([student_id, amount, payment_date, payment_method, status]):
                messages.error(request, "Error: All fields are required.")
            else:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO smsapp_feepayment (student_id, amount, payment_date, payment_method, status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (student_id, amount, payment_date, payment_method, status))
                    conn.commit()
                messages.success(request, "Fee Payment Added Successfully!")
                return redirect('view_fees')
    finally:
        conn.close()

    return render(request, 'add_fee.html', {'students': students})


@login_required(login_url='login')
def view_fees_view(request):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT fp.id, fp.amount, fp.payment_date, fp.payment_method, fp.status,
                       s.id AS student_id, s.first_name, s.last_name, s.roll_number
                FROM smsapp_feepayment fp
                JOIN smsapp_student s ON fp.student_id = s.id
                ORDER BY fp.payment_date DESC
            """)
            rows = cur.fetchall()
    finally:
        conn.close()

    fee_payments = []
    for row in rows:
        fee_payments.append(R({
            'id': row['id'],
            'amount': row['amount'],
            'payment_date': row['payment_date'],
            'payment_method': row['payment_method'],
            'status': row['status'],
            'student': {
                'id': row['student_id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'roll_number': row['roll_number'],
            }
        }))

    return render(request, 'view_fees.html', {'fee_payments': fee_payments})


@login_required(login_url='login')
def update_fee_view(request, id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Fetch fee payment with student info via JOIN
            cur.execute("""
                SELECT fp.id, fp.amount, fp.payment_date, fp.payment_method, fp.status,
                       s.id AS student_id, s.first_name, s.last_name, s.roll_number
                FROM smsapp_feepayment fp
                JOIN smsapp_student s ON fp.student_id = s.id
                WHERE fp.id = %s
            """, (id,))
            row = cur.fetchone()
            if not row:
                messages.error(request, "Fee record not found.")
                return redirect('view_fees')

            fee_payment = R({
                'id': row['id'],
                'amount': row['amount'],
                'payment_date': row['payment_date'],
                'payment_method': row['payment_method'],
                'status': row['status'],
                'student': {
                    'id': row['student_id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'roll_number': row['roll_number'],
                }
            })

            cur.execute("SELECT * FROM smsapp_student ORDER BY first_name, last_name")
            students = _fetch_all(cur)

        if request.method == 'POST':
            new_student_id  = request.POST.get('student')
            new_amount      = request.POST.get('amount')
            new_date        = request.POST.get('payment_date')
            new_method      = request.POST.get('payment_method')
            new_status      = request.POST.get('status')

            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE smsapp_feepayment
                    SET student_id = %s, amount = %s, payment_date = %s, payment_method = %s, status = %s
                    WHERE id = %s
                """, (new_student_id, new_amount, new_date, new_method, new_status, id))
                conn.commit()
            messages.success(request, "Fee Payment Updated Successfully!")
            return redirect('view_fees')
    finally:
        conn.close()

    return render(request, 'update_fee.html', {'fee_payment': fee_payment, 'students': students})


@login_required(login_url='login')
def delete_fee_view(request, id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM smsapp_feepayment WHERE id = %s", (id,))
            conn.commit()
    finally:
        conn.close()
    messages.success(request, "Fee Payment Deleted Successfully!")
    return redirect('view_fees')


@login_required(login_url='login')
def search_fee_view(request):
    query = request.GET.get('query', '').strip()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if query:
                cur.execute("""
                    SELECT fp.id, fp.amount, fp.payment_date, fp.payment_method, fp.status,
                           s.id AS student_id, s.first_name, s.last_name, s.roll_number
                    FROM smsapp_feepayment fp
                    JOIN smsapp_student s ON fp.student_id = s.id
                    WHERE s.roll_number LIKE %s
                       OR s.first_name  LIKE %s
                       OR s.last_name   LIKE %s
                       OR fp.status     LIKE %s
                    ORDER BY fp.payment_date DESC
                """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                cur.execute("""
                    SELECT fp.id, fp.amount, fp.payment_date, fp.payment_method, fp.status,
                           s.id AS student_id, s.first_name, s.last_name, s.roll_number
                    FROM smsapp_feepayment fp
                    JOIN smsapp_student s ON fp.student_id = s.id
                    ORDER BY fp.payment_date DESC
                """)
            rows = cur.fetchall()
    finally:
        conn.close()

    fee_payments = []
    for row in rows:
        fee_payments.append(R({
            'id': row['id'],
            'amount': row['amount'],
            'payment_date': row['payment_date'],
            'payment_method': row['payment_method'],
            'status': row['status'],
            'student': {
                'id': row['student_id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'roll_number': row['roll_number'],
            }
        }))

    return render(request, 'search_fee.html', {'fee_payments': fee_payments, 'query': query})


@login_required(login_url='login')
def fee_receipt_view(request, id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT fp.id, fp.amount, fp.payment_date, fp.payment_method, fp.status,
                       s.id AS student_id, s.first_name, s.last_name, s.roll_number,
                       s.department, s.year, s.semester
                FROM smsapp_feepayment fp
                JOIN smsapp_student s ON fp.student_id = s.id
                WHERE fp.id = %s
            """, (id,))
            row = cur.fetchone()
            if not row:
                messages.error(request, "Fee record not found.")
                return redirect('view_fees')

            fee_payment = R({
                'id': row['id'],
                'amount': row['amount'],
                'payment_date': row['payment_date'],
                'payment_method': row['payment_method'],
                'status': row['status'],
                'student': {
                    'id': row['student_id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'roll_number': row['roll_number'],
                    'department': row['department'],
                    'year': row['year'],
                    'semester': row['semester'],
                }
            })
    finally:
        conn.close()

    return render(request, 'fee_receipt.html', {'fee_payment': fee_payment})


# ================================================================
# ATTENDANCE
# ================================================================

@login_required(login_url='login')
def add_attendance_view(request):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM smsapp_student ORDER BY first_name, last_name")
            students = _fetch_all(cur)

        if request.method == 'POST':
            attendance_date = request.POST.get('attendance_date')
            if not attendance_date:
                messages.error(request, "Please select attendance date.")
            else:
                with conn.cursor() as cur:
                    for student in students:
                        status = request.POST.get(f'status_{student.id}')
                        if status:
                            # DELETE existing record for same student+date, then INSERT fresh
                            cur.execute(
                                "DELETE FROM smsapp_attendance WHERE student_id = %s AND attendance_date = %s",
                                (student.id, attendance_date)
                            )
                            cur.execute(
                                "INSERT INTO smsapp_attendance (student_id, attendance_date, status) VALUES (%s, %s, %s)",
                                (student.id, attendance_date, status)
                            )
                    conn.commit()
                messages.success(request, "Attendance Saved Successfully!")
                return redirect('view_attendance')
    finally:
        conn.close()

    return render(request, 'add_attendance.html', {'students': students})


@login_required(login_url='login')
def view_attendance_view(request):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Date-wise attendance logs (JOIN for student name)
            cur.execute("""
                SELECT att.id, att.attendance_date, att.status,
                       s.id AS student_id, s.first_name, s.last_name, s.roll_number
                FROM smsapp_attendance att
                JOIN smsapp_student s ON att.student_id = s.id
                ORDER BY att.attendance_date DESC, s.first_name ASC
            """)
            att_rows = cur.fetchall()
            attendance_records = []
            for row in att_rows:
                attendance_records.append(R({
                    'id': row['id'],
                    'attendance_date': row['attendance_date'],
                    'status': row['status'],
                    'student': {
                        'id': row['student_id'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'roll_number': row['roll_number'],
                    }
                }))

            # Attendance summary per student using GROUP BY
            cur.execute("""
                SELECT s.id, s.first_name, s.last_name, s.roll_number,
                       COUNT(att.id) AS total_days,
                       SUM(CASE WHEN att.status = 'Present' THEN 1 ELSE 0 END) AS present_days
                FROM smsapp_student s
                LEFT JOIN smsapp_attendance att ON s.id = att.student_id
                GROUP BY s.id, s.first_name, s.last_name, s.roll_number
                ORDER BY s.first_name
            """)
            summary_rows = cur.fetchall()
            attendance_summary = []
            for row in summary_rows:
                total = row['total_days'] or 0
                present = row['present_days'] or 0
                percentage = round((present / total) * 100) if total > 0 else 0
                attendance_summary.append(R({
                    'student': {
                        'id': row['id'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'roll_number': row['roll_number'],
                    },
                    'total_days': total,
                    'present_days': present,
                    'percentage': percentage,
                }))
    finally:
        conn.close()

    return render(request, 'view_attendance.html', {
        'attendance_records': attendance_records,
        'attendance_summary': attendance_summary,
    })


# ================================================================
# MARKS
# ================================================================

@login_required(login_url='login')
def add_marks_view(request):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM smsapp_student ORDER BY first_name, last_name")
            students = _fetch_all(cur)

        if request.method == 'POST':
            student_id     = request.POST.get('student')
            subject        = request.POST.get('subject', '').strip()
            marks_obtained = request.POST.get('marks_obtained')
            total_marks    = request.POST.get('total_marks')

            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO smsapp_mark (student_id, subject, marks_obtained, total_marks)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, subject, marks_obtained, total_marks))
                conn.commit()
            messages.success(request, "Marks Added Successfully!")
            return redirect('add_marks')
    finally:
        conn.close()

    return render(request, 'add_marks.html', {'students': students})


# ================================================================
# DEPARTMENTS
# ================================================================

@login_required(login_url='login')
def departments_view(request):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT department FROM smsapp_student ORDER BY department")
            rows = cur.fetchall()
            departments = [R(row) for row in rows]
    finally:
        conn.close()
    return render(request, 'departments.html', {'departments': departments})


# ================================================================
# STATIC PAGES
# ================================================================

def about_view(request):
    return render(request, 'about.html')


def contact_view(request):
    return render(request, 'contact.html')


# ================================================================
# STUDENT PORTAL VIEWS
# ================================================================

def student_login_view(request):
    if 'student_id' in request.session:
        return redirect('student_dashboard')

    error_msg = None
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number', '').strip()
        password    = request.POST.get('password', '').strip()
        if not roll_number or not password:
            error_msg = "Please enter both Roll Number and Password."
        else:
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM smsapp_student WHERE roll_number = %s AND password = %s",
                        (roll_number, password)
                    )
                    row = cur.fetchone()
            finally:
                conn.close()

            if row:
                request.session['student_id'] = row['id']
                return redirect('student_dashboard')
            else:
                error_msg = "Invalid Roll Number or Password!"

    return render(request, 'index.html', {'error_msg': error_msg})


def student_register_view(request):
    if request.method == 'POST':
        roll_number   = request.POST.get('roll_number', '').strip()
        first_name    = request.POST.get('first_name', '').strip()
        last_name     = request.POST.get('last_name', '').strip()
        department    = request.POST.get('department', '').strip()
        year          = request.POST.get('year', 'First Year').strip()
        email         = request.POST.get('email', '').strip()
        password      = request.POST.get('password', '').strip()
        profile_image = request.FILES.get('profile_image')

        # Optional fields with defaults
        gender   = request.POST.get('gender', 'Male').strip()
        dob      = request.POST.get('dob', '2002-01-01').strip()
        semester = request.POST.get('semester', 'Semester 1').strip()
        phone    = request.POST.get('phone', '9876543210').strip()
        address  = request.POST.get('address', 'College Campus').strip()

        if not all([roll_number, first_name, last_name, department, email, password]):
            messages.error(request, "Error: Please fill in all required fields.")
            return render(request, 'student_register.html')

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM smsapp_student WHERE roll_number = %s", (roll_number,))
                if cur.fetchone():
                    messages.error(request, f"Error: Student with Roll Number '{roll_number}' already exists.")
                    return render(request, 'student_register.html')

                # Save profile image if uploaded
                image_name = None
                if profile_image:
                    import os
                    from django.conf import settings
                    upload_dir = settings.MEDIA_ROOT / 'student_images'
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    image_name = 'student_images/' + profile_image.name
                    with open(settings.MEDIA_ROOT / image_name, 'wb') as f:
                        for chunk in profile_image.chunks():
                            f.write(chunk)

                cur.execute("""
                    INSERT INTO smsapp_student
                        (roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password, profile_image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password, image_name))
                conn.commit()

                # Get the new student's ID
                cur.execute("SELECT id FROM smsapp_student WHERE roll_number = %s", (roll_number,))
                new_id = cur.fetchone()['id']

        finally:
            conn.close()

        request.session['student_id'] = new_id
        messages.success(request, "Registration Successful! Welcome to your student portal.")
        return redirect('student_dashboard')

    return render(request, 'student_register.html')


def student_dashboard_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM smsapp_student WHERE id = %s", (student_id,))
            student = _fetch_one(cur)
            if not student:
                del request.session['student_id']
                return redirect('student_login')

            # Attendance records
            cur.execute("""
                SELECT * FROM smsapp_attendance
                WHERE student_id = %s
                ORDER BY attendance_date DESC
            """, (student_id,))
            attendance_records = _fetch_all(cur)
            total_days = len(attendance_records)
            present_days  = sum(1 for r in attendance_records if r.status == 'Present')
            absent_days   = sum(1 for r in attendance_records if r.status == 'Absent')
            attendance_percentage = round((present_days / total_days) * 100) if total_days > 0 else 0

            # Fee payments
            cur.execute("""
                SELECT * FROM smsapp_feepayment
                WHERE student_id = %s
                ORDER BY payment_date DESC
            """, (student_id,))
            fee_payments = _fetch_all(cur)
            total_fees_paid = sum(float(p.amount) for p in fee_payments if p.status == 'Paid')

            # Marks
            cur.execute(
                "SELECT * FROM smsapp_mark WHERE student_id = %s",
                (student_id,)
            )
            marks = _fetch_all(cur)
    finally:
        conn.close()

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

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM smsapp_student WHERE id = %s", (student_id,))
            student = _fetch_one(cur)
            if not student:
                return redirect('student_login')

        if request.method == 'POST':
            amount         = request.POST.get('amount')
            payment_method = request.POST.get('payment_method')

            if not amount or not payment_method:
                messages.error(request, "Please fill in all details.")
                return render(request, 'student_pay_fee.html', {'student': student})

            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO smsapp_feepayment (student_id, amount, payment_date, payment_method, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (student_id, amount, date.today(), payment_method, 'Paid'))
                conn.commit()

            messages.success(request, "Fee Payment Completed Successfully!")
            return redirect('student_dashboard')
    finally:
        conn.close()

    return render(request, 'student_pay_fee.html', {'student': student})


def student_logout_view(request):
    if 'student_id' in request.session:
        del request.session['student_id']
    return redirect('student_login')
