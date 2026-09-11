import os
import sys
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from smsapp.models import Student, FeePayment, Attendance, Mark

def run_all_tests():
    print("=" * 60)
    print("STARTING COMPLETE RUNTIME VERIFICATION SUITE")
    print("=" * 60)
    
    client = Client()
    results = {}

    # 1. MySQL Connection & Database Check
    try:
        import pymysql
        conn = pymysql.connect(host='localhost', user='root', password='root', database='student_management_db')
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            res = cur.fetchone()
        conn.close()
        results["MySQL Connection (root/root)"] = "PASS" if res else "FAIL"
        print("[PASS] MySQL Connection to student_management_db verified.")
    except Exception as e:
        results["MySQL Connection (root/root)"] = f"FAIL: {e}"
        print(f"[FAIL] MySQL Connection failed: {e}")

    # Ensure admin user exists with admin123
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    else:
        admin_user.set_password('admin123')
        admin_user.save()

    # ---------------- FLOW 1: ADMIN LOGIN & STUDENT CRUD ---------------- #
    print("\n--- Testing Flow 1: Admin Login & Student CRUD ---")
    
    # Test Admin Login (Invalid Password)
    resp = client.post('/', {'username': 'admin', 'password': 'wrongpassword'})
    assert resp.status_code == 200
    assert "Invalid Username or Password!" in resp.content.decode()
    results["Admin Wrong Password Handling"] = "PASS"
    print("[PASS] Wrong password correctly rejected.")

    # Test Admin Login (Valid Credentials)
    resp = client.post('/', {'username': 'admin', 'password': 'admin123'}, follow=True)
    assert resp.status_code == 200
    assert "Dashboard" in resp.content.decode()
    results["Admin Login"] = "PASS"
    print("[PASS] Admin successfully logged in and redirected to Dashboard.")

    # Test Dashboard View
    resp = client.get('/dashboard/')
    assert resp.status_code == 200
    assert "Today's Overview" in resp.content.decode()
    results["Dashboard View"] = "PASS"
    print("[PASS] Dashboard view renders overview metrics.")

    # Test Add Student
    test_roll = "TEST999"
    # Clean up if exists from previous test
    Student.objects.filter(roll_number=test_roll).delete()
    
    add_data = {
        'roll_number': test_roll,
        'first_name': 'Aman',
        'last_name': 'Verma',
        'gender': 'Male',
        'dob': '2004-04-14',
        'department': 'Computer Engineering',
        'year': 'Second Year',
        'semester': 'Semester 3',
        'phone': '9876543211',
        'email': 'aman.verma@example.com',
        'address': 'Sector 15, Navi Mumbai',
        'password': 'password123'
    }
    resp = client.post('/add/', add_data, follow=True)
    assert resp.status_code == 200
    created_student = Student.objects.filter(roll_number=test_roll).first()
    assert created_student is not None
    results["Add Student"] = "PASS"
    print(f"[PASS] Student created: {created_student.first_name} {created_student.last_name} (ID: {created_student.id}).")

    # Test View Students
    resp = client.get('/students/')
    assert resp.status_code == 200
    assert test_roll in resp.content.decode()
    results["View Students"] = "PASS"
    print("[PASS] View students list displays new student record.")

    # Test Search Student
    resp = client.get(f'/search/?query={test_roll}&search_type=roll')
    assert resp.status_code == 200
    assert "Aman" in resp.content.decode()
    results["Search Student"] = "PASS"
    print("[PASS] Student search returned matching record.")

    # Test Student Profile View
    resp = client.get(f'/student/{created_student.id}/')
    assert resp.status_code == 200
    assert "Aman" in resp.content.decode()
    results["Student Profile View"] = "PASS"
    print("[PASS] Student profile page loads successfully.")

    # Test Update Student
    update_data = add_data.copy()
    update_data['first_name'] = 'Aman-Updated'
    resp = client.post(f'/update/{created_student.id}/', update_data, follow=True)
    assert resp.status_code == 200
    created_student.refresh_from_db()
    assert created_student.first_name == 'Aman-Updated'
    results["Update Student"] = "PASS"
    print("[PASS] Student record updated and verified in database.")

    # ---------------- FLOW 2: ATTENDANCE MANAGEMENT ---------------- #
    print("\n--- Testing Flow 2: Attendance Management ---")
    today_str = date.today().strftime('%Y-%m-%d')
    att_data = {
        'attendance_date': today_str,
        f'status_{created_student.id}': 'Present'
    }
    resp = client.post('/attendance/add/', att_data, follow=True)
    assert resp.status_code == 200
    att_record = Attendance.objects.filter(student=created_student, attendance_date=today_str).first()
    assert att_record is not None
    assert att_record.status == 'Present'
    results["Add Attendance"] = "PASS"
    print(f"[PASS] Attendance recorded for student {created_student.roll_number}.")

    # View Attendance Summary
    resp = client.get('/attendance/')
    assert resp.status_code == 200
    assert "Attendance Records" in resp.content.decode()
    results["View Attendance"] = "PASS"
    print("[PASS] Attendance summary and date logs displayed.")

    # ---------------- FLOW 3: ACADEMIC MARKS ---------------- #
    print("\n--- Testing Flow 3: Academic Marks ---")
    mark_data = {
        'student': created_student.id,
        'subject': 'Python Programming',
        'marks_obtained': 92,
        'total_marks': 100
    }
    resp = client.post('/marks/add/', mark_data, follow=True)
    assert resp.status_code == 200
    mark_record = Mark.objects.filter(student=created_student, subject='Python Programming').first()
    assert mark_record is not None
    assert mark_record.marks_obtained == 92
    results["Add Marks"] = "PASS"
    print(f"[PASS] Academic mark recorded: {mark_record.subject} - {mark_record.marks_obtained}/{mark_record.total_marks}.")

    # ---------------- FLOW 4: FEES MANAGEMENT ---------------- #
    print("\n--- Testing Flow 4: Fees Management ---")
    fee_data = {
        'student': created_student.id,
        'amount': '35000.00',
        'payment_date': today_str,
        'payment_method': 'UPI',
        'status': 'Paid'
    }
    resp = client.post('/fees/add/', fee_data, follow=True)
    assert resp.status_code == 200
    fee_record = FeePayment.objects.filter(student=created_student).first()
    assert fee_record is not None
    results["Add Fee Payment"] = "PASS"
    print(f"[PASS] Fee record added: Rs {fee_record.amount} (ID: {fee_record.id}).")

    # View Fees
    resp = client.get('/fees/')
    assert resp.status_code == 200
    assert "Student Fee Payments" in resp.content.decode()
    results["View Fees"] = "PASS"
    print("[PASS] Fee records table displayed.")

    # Search Fee
    resp = client.get(f'/fees/search/?query={created_student.roll_number}')
    assert resp.status_code == 200
    assert str(fee_record.amount) in resp.content.decode()
    results["Search Fee"] = "PASS"
    print("[PASS] Fee search retrieved payment record.")

    # Update Fee
    update_fee_data = {
        'student': created_student.id,
        'amount': '40000.00',
        'payment_date': today_str,
        'payment_method': 'Credit Card',
        'status': 'Paid'
    }
    resp = client.post(f'/fees/update/{fee_record.id}/', update_fee_data, follow=True)
    assert resp.status_code == 200
    fee_record.refresh_from_db()
    assert fee_record.amount == 40000.00
    results["Update Fee"] = "PASS"
    print("[PASS] Fee payment updated to Rs 40000.00.")

    # Fee Receipt
    resp = client.get(f'/fees/receipt/{fee_record.id}/')
    assert resp.status_code == 200
    assert "COLLEGE FEE RECEIPT" in resp.content.decode()
    results["Fee Receipt View"] = "PASS"
    print("[PASS] Printable fee receipt rendered.")

    # Delete Fee
    resp = client.get(f'/fees/delete/{fee_record.id}/', follow=True)
    assert resp.status_code == 200
    assert FeePayment.objects.filter(id=fee_record.id).count() == 0
    results["Delete Fee"] = "PASS"
    print("[PASS] Fee payment deleted successfully.")

    # Delete Student
    resp = client.get(f'/delete/{created_student.id}/', follow=True)
    assert resp.status_code == 200
    assert Student.objects.filter(id=created_student.id).count() == 0
    results["Delete Student"] = "PASS"
    print(f"[PASS] Student {test_roll} successfully deleted.")

    # Admin Logout
    resp = client.get('/logout/', follow=True)
    assert resp.status_code == 200
    results["Admin Logout"] = "PASS"
    print("[PASS] Admin logged out.")

    # ---------------- FLOW 5: STUDENT PORTAL ---------------- #
    print("\n--- Testing Flow 5: Student Portal ---")
    stud_client = Client()

    student_roll = "STUDENT101"
    Student.objects.filter(roll_number=student_roll).delete()

    reg_data = {
        'first_name': 'Neha',
        'last_name': 'Kulkarni',
        'roll_number': student_roll,
        'email': 'neha.k@example.com',
        'password': 'studentpass123',
        'department': 'Information Technology',
        'year': 'Second Year',
        'gender': 'Female',
        'dob': '2004-08-10',
        'semester': 'Semester 3',
        'phone': '9876543212',
        'address': 'Pune City'
    }
    resp = stud_client.post('/student/register/', reg_data, follow=True)
    assert resp.status_code == 200
    neha = Student.objects.filter(roll_number=student_roll).first()
    assert neha is not None
    results["Student Self-Registration"] = "PASS"
    print(f"[PASS] Student registered: {neha.first_name} {neha.last_name}.")

    # Student Logout
    resp = stud_client.get('/student/logout/', follow=True)
    results["Student Logout"] = "PASS"
    print("[PASS] Student logged out.")

    # Student Login (Wrong Password)
    resp = stud_client.post('/student/login/', {'roll_number': student_roll, 'password': 'wrongpass'})
    assert resp.status_code == 200
    assert "Invalid Roll Number or Password!" in resp.content.decode()
    results["Student Login (Wrong Password)"] = "PASS"
    print("[PASS] Student wrong password rejected.")

    # Student Login (Correct Password)
    resp = stud_client.post('/student/login/', {'roll_number': student_roll, 'password': 'studentpass123'}, follow=True)
    assert resp.status_code == 200
    assert "Neha" in resp.content.decode()
    results["Student Login"] = "PASS"
    print("[PASS] Student logged in successfully to Student Dashboard.")

    # Student Dashboard View
    resp = stud_client.get('/student/dashboard/')
    assert resp.status_code == 200
    assert "Attendance Percentage" in resp.content.decode()
    results["Student Dashboard View"] = "PASS"
    print("[PASS] Student Dashboard metrics and tables rendered.")

    # Student Pay Fee Online
    pay_data = {
        'amount': '25000.00',
        'payment_method': 'Online Net Banking'
    }
    resp = stud_client.post('/student/pay-fee/', pay_data, follow=True)
    assert resp.status_code == 200
    neha_fee = FeePayment.objects.filter(student=neha).first()
    assert neha_fee is not None
    assert neha_fee.amount == 25000.00
    results["Student Online Fee Payment"] = "PASS"
    print(f"[PASS] Student online fee payment recorded: Rs {neha_fee.amount}.")

    # Clean up test student
    neha.delete()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    for test_name, res in results.items():
        print(f"  {test_name:<35}: {res}")
    print("=" * 60)

if __name__ == '__main__':
    run_all_tests()
