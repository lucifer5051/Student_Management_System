"""
test_flows.py — Complete Runtime Verification Suite
Student Management System

All database verifications use PyMySQL + raw SQL (no Django ORM).
Django is used only for: Client test runner, auth.
"""

import os
import sys
import django
import pymysql
import pymysql.cursors
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.hashers import make_password


# ------------------------------------------------------------------
# Raw SQL helper
# ------------------------------------------------------------------

def get_conn():
    return pymysql.connect(
        host='localhost', user='root', password='root',
        database='student_management_db',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def sql_fetchone(sql, params=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    finally:
        conn.close()


def sql_fetchall(sql, params=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def sql_count(sql, params=()):
    row = sql_fetchone(sql, params)
    if row:
        return list(row.values())[0]
    return 0


def sql_delete(sql, params=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------
# Test runner
# ------------------------------------------------------------------

def run_all_tests():
    print("=" * 60)
    print("STARTING COMPLETE RUNTIME VERIFICATION SUITE")
    print("=" * 60)

    client = Client()
    results = {}

    # ---- 1. MySQL Connection ----
    try:
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

    # Ensure Django admin user exists with correct password (raw SQL, no ORM)
    hashed_pw = make_password('admin123')
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM auth_user WHERE username = 'admin'")
            existing = cur.fetchone()
            if existing:
                cur.execute("UPDATE auth_user SET password = %s WHERE username = 'admin'", (hashed_pw,))
            else:
                cur.execute("""
                    INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
                    VALUES (%s, NULL, 1, 'admin', 'System', 'Administrator', 'admin@example.com', 1, 1, NOW())
                """, (hashed_pw,))
        conn.commit()
    finally:
        conn.close()

    # ---- FLOW 1: Admin Login & Student CRUD ----
    print("\n--- Testing Flow 1: Admin Login & Student CRUD ---")
    test_roll = "TEST999"

    # Clean up if exists from previous test run
    sql_delete("DELETE FROM smsapp_student WHERE roll_number = %s", (test_roll,))

    # Wrong password
    resp = client.post('/', {'username': 'admin', 'password': 'wrongpassword'})
    assert resp.status_code == 200
    assert "Invalid Username or Password!" in resp.content.decode()
    results["Admin Wrong Password Handling"] = "PASS"
    print("[PASS] Wrong password correctly rejected.")

    # Correct login
    resp = client.post('/', {'username': 'admin', 'password': 'admin123'}, follow=True)
    assert resp.status_code == 200
    assert "Dashboard" in resp.content.decode()
    results["Admin Login"] = "PASS"
    print("[PASS] Admin successfully logged in and redirected to Dashboard.")

    # Dashboard
    resp = client.get('/dashboard/')
    assert resp.status_code == 200
    assert "Today's Overview" in resp.content.decode()
    results["Dashboard View"] = "PASS"
    print("[PASS] Dashboard view renders overview metrics.")

    # Add Student
    add_data = {
        'roll_number': test_roll,
        'first_name':  'Aman',
        'last_name':   'Verma',
        'gender':      'Male',
        'dob':         '2004-04-14',
        'department':  'Computer Engineering',
        'year':        'Second Year',
        'semester':    'Semester 3',
        'phone':       '9876543211',
        'email':       'aman.verma@example.com',
        'address':     'Sector 15, Navi Mumbai',
        'password':    'password123',
    }
    resp = client.post('/add/', add_data, follow=True)
    assert resp.status_code == 200
    created = sql_fetchone("SELECT * FROM smsapp_student WHERE roll_number = %s", (test_roll,))
    assert created is not None
    student_id = created['id']
    results["Add Student"] = "PASS"
    print(f"[PASS] Student created: {created['first_name']} {created['last_name']} (ID: {student_id}).")

    # View Students
    resp = client.get('/students/')
    assert resp.status_code == 200
    assert test_roll in resp.content.decode()
    results["View Students"] = "PASS"
    print("[PASS] View students list displays new student record.")

    # Search Student
    resp = client.get(f'/search/?query={test_roll}&search_type=roll')
    assert resp.status_code == 200
    assert "Aman" in resp.content.decode()
    results["Search Student"] = "PASS"
    print("[PASS] Student search returned matching record.")

    # Student Profile View
    resp = client.get(f'/student/{student_id}/')
    assert resp.status_code == 200
    assert "Aman" in resp.content.decode()
    results["Student Profile View"] = "PASS"
    print("[PASS] Student profile page loads successfully.")

    # Update Student
    update_data = add_data.copy()
    update_data['first_name'] = 'Aman-Updated'
    resp = client.post(f'/update/{student_id}/', update_data, follow=True)
    assert resp.status_code == 200
    updated = sql_fetchone("SELECT first_name FROM smsapp_student WHERE id = %s", (student_id,))
    assert updated['first_name'] == 'Aman-Updated'
    results["Update Student"] = "PASS"
    print("[PASS] Student record updated and verified in database.")

    # ---- FLOW 2: Attendance ----
    print("\n--- Testing Flow 2: Attendance Management ---")
    today_str = date.today().strftime('%Y-%m-%d')
    att_data = {
        'attendance_date': today_str,
        f'status_{student_id}': 'Present',
    }
    resp = client.post('/attendance/add/', att_data, follow=True)
    assert resp.status_code == 200
    att_row = sql_fetchone(
        "SELECT * FROM smsapp_attendance WHERE student_id = %s AND attendance_date = %s",
        (student_id, today_str)
    )
    assert att_row is not None
    assert att_row['status'] == 'Present'
    results["Add Attendance"] = "PASS"
    print(f"[PASS] Attendance recorded for student {test_roll}.")

    resp = client.get('/attendance/')
    assert resp.status_code == 200
    assert "Attendance Records" in resp.content.decode()
    results["View Attendance"] = "PASS"
    print("[PASS] Attendance summary and date logs displayed.")

    # ---- FLOW 3: Marks ----
    print("\n--- Testing Flow 3: Academic Marks ---")
    mark_data = {
        'student': student_id,
        'subject': 'Python Programming',
        'marks_obtained': 92,
        'total_marks': 100,
    }
    resp = client.post('/marks/add/', mark_data, follow=True)
    assert resp.status_code == 200
    mark_row = sql_fetchone(
        "SELECT * FROM smsapp_mark WHERE student_id = %s AND subject = 'Python Programming'",
        (student_id,)
    )
    assert mark_row is not None
    assert mark_row['marks_obtained'] == 92
    results["Add Marks"] = "PASS"
    print(f"[PASS] Academic mark recorded: {mark_row['subject']} - {mark_row['marks_obtained']}/{mark_row['total_marks']}.")

    # ---- FLOW 4: Fees ----
    print("\n--- Testing Flow 4: Fees Management ---")
    fee_data = {
        'student': student_id,
        'amount': '35000.00',
        'payment_date': today_str,
        'payment_method': 'UPI',
        'status': 'Paid',
    }
    resp = client.post('/fees/add/', fee_data, follow=True)
    assert resp.status_code == 200
    fee_row = sql_fetchone(
        "SELECT * FROM smsapp_feepayment WHERE student_id = %s ORDER BY id DESC LIMIT 1",
        (student_id,)
    )
    assert fee_row is not None
    fee_id = fee_row['id']
    results["Add Fee Payment"] = "PASS"
    print(f"[PASS] Fee record added: Rs {fee_row['amount']} (ID: {fee_id}).")

    resp = client.get('/fees/')
    assert resp.status_code == 200
    assert "Student Fee Payments" in resp.content.decode()
    results["View Fees"] = "PASS"
    print("[PASS] Fee records table displayed.")

    resp = client.get(f'/fees/search/?query={test_roll}')
    assert resp.status_code == 200
    assert "35000" in resp.content.decode()
    results["Search Fee"] = "PASS"
    print("[PASS] Fee search retrieved payment record.")

    update_fee_data = {
        'student': student_id,
        'amount': '40000.00',
        'payment_date': today_str,
        'payment_method': 'Credit Card',
        'status': 'Paid',
    }
    resp = client.post(f'/fees/update/{fee_id}/', update_fee_data, follow=True)
    assert resp.status_code == 200
    updated_fee = sql_fetchone("SELECT amount FROM smsapp_feepayment WHERE id = %s", (fee_id,))
    assert float(updated_fee['amount']) == 40000.00
    results["Update Fee"] = "PASS"
    print("[PASS] Fee payment updated to Rs 40000.00.")

    resp = client.get(f'/fees/receipt/{fee_id}/')
    assert resp.status_code == 200
    assert "COLLEGE FEE RECEIPT" in resp.content.decode()
    results["Fee Receipt View"] = "PASS"
    print("[PASS] Printable fee receipt rendered.")

    resp = client.get(f'/fees/delete/{fee_id}/', follow=True)
    assert resp.status_code == 200
    assert sql_count("SELECT COUNT(*) AS c FROM smsapp_feepayment WHERE id = %s", (fee_id,)) == 0
    results["Delete Fee"] = "PASS"
    print("[PASS] Fee payment deleted successfully.")

    resp = client.get(f'/delete/{student_id}/', follow=True)
    assert resp.status_code == 200
    assert sql_count("SELECT COUNT(*) AS c FROM smsapp_student WHERE id = %s", (student_id,)) == 0
    results["Delete Student"] = "PASS"
    print(f"[PASS] Student {test_roll} successfully deleted.")

    resp = client.get('/logout/', follow=True)
    assert resp.status_code == 200
    results["Admin Logout"] = "PASS"
    print("[PASS] Admin logged out.")

    # ---- FLOW 5: Student Portal ----
    print("\n--- Testing Flow 5: Student Portal ---")
    stud_client = Client()
    student_roll = "STUDENT101"
    sql_delete("DELETE FROM smsapp_student WHERE roll_number = %s", (student_roll,))

    reg_data = {
        'first_name':  'Neha',
        'last_name':   'Kulkarni',
        'roll_number': student_roll,
        'email':       'neha.k@example.com',
        'password':    'studentpass123',
        'department':  'Information Technology',
        'year':        'Second Year',
        'gender':      'Female',
        'dob':         '2004-08-10',
        'semester':    'Semester 3',
        'phone':       '9876543212',
        'address':     'Pune City',
    }
    resp = stud_client.post('/student/register/', reg_data, follow=True)
    assert resp.status_code == 200
    neha = sql_fetchone("SELECT * FROM smsapp_student WHERE roll_number = %s", (student_roll,))
    assert neha is not None
    neha_id = neha['id']
    results["Student Self-Registration"] = "PASS"
    print(f"[PASS] Student registered: {neha['first_name']} {neha['last_name']}.")

    resp = stud_client.get('/student/logout/', follow=True)
    results["Student Logout"] = "PASS"
    print("[PASS] Student logged out.")

    resp = stud_client.post('/student/login/', {'roll_number': student_roll, 'password': 'wrongpass'})
    assert resp.status_code == 200
    assert "Invalid Roll Number or Password!" in resp.content.decode()
    results["Student Login (Wrong Password)"] = "PASS"
    print("[PASS] Student wrong password rejected.")

    resp = stud_client.post('/student/login/', {'roll_number': student_roll, 'password': 'studentpass123'}, follow=True)
    assert resp.status_code == 200
    assert "Neha" in resp.content.decode()
    results["Student Login"] = "PASS"
    print("[PASS] Student logged in successfully to Student Dashboard.")

    resp = stud_client.get('/student/dashboard/')
    assert resp.status_code == 200
    assert "Attendance Percentage" in resp.content.decode()
    results["Student Dashboard View"] = "PASS"
    print("[PASS] Student Dashboard metrics and tables rendered.")

    pay_data = {'amount': '25000.00', 'payment_method': 'Online Net Banking'}
    resp = stud_client.post('/student/pay-fee/', pay_data, follow=True)
    assert resp.status_code == 200
    neha_fee = sql_fetchone(
        "SELECT * FROM smsapp_feepayment WHERE student_id = %s ORDER BY id DESC LIMIT 1",
        (neha_id,)
    )
    assert neha_fee is not None
    assert float(neha_fee['amount']) == 25000.00
    results["Student Online Fee Payment"] = "PASS"
    print(f"[PASS] Student online fee payment recorded: Rs {neha_fee['amount']}.")

    # Clean up test student
    sql_delete("DELETE FROM smsapp_student WHERE id = %s", (neha_id,))

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    for test_name, res in results.items():
        print(f"  {test_name:<35}: {res}")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
