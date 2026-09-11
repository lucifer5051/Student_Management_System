import pymysql
try:
    from .db import get_connection
except ImportError:
    from db import get_connection

def add_student(roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address):
    connection = get_connection()
    if not connection:
        return False
    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO smsapp_student (roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '123456')"""
            cursor.execute(sql, (roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address))
            connection.commit()
            return True
    except Exception as e:
        print(f"Error adding student: {e}")
        return False
    finally:
        connection.close()

def get_all_students():
    connection = get_connection()
    if not connection:
        return []
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM smsapp_student ORDER BY id DESC"
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching students: {e}")
        return []
    finally:
        connection.close()

def update_student(student_id, roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address):
    connection = get_connection()
    if not connection:
        return False
    try:
        with connection.cursor() as cursor:
            sql = """UPDATE smsapp_student 
                     SET roll_number=%s, first_name=%s, last_name=%s, gender=%s, dob=%s, department=%s, year=%s, semester=%s, phone=%s, email=%s, address=%s 
                     WHERE id=%s"""
            cursor.execute(sql, (roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, student_id))
            connection.commit()
            return True
    except Exception as e:
        print(f"Error updating student: {e}")
        return False
    finally:
        connection.close()

def delete_student(student_id):
    connection = get_connection()
    if not connection:
        return False
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM smsapp_student WHERE id=%s"
            cursor.execute(sql, (student_id,))
            connection.commit()
            return True
    except Exception as e:
        print(f"Error deleting student: {e}")
        return False
    finally:
        connection.close()
