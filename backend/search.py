import pymysql
try:
    from .db import get_connection
except ImportError:
    from db import get_connection

def search_students(search_by, keyword):
    connection = get_connection()
    if not connection:
        return []
    try:
        with connection.cursor() as cursor:
            like_term = f"%{keyword}%"
            if search_by == 'roll':
                sql = "SELECT * FROM smsapp_student WHERE roll_number LIKE %s"
                cursor.execute(sql, (like_term,))
            elif search_by == 'dept':
                sql = "SELECT * FROM smsapp_student WHERE department LIKE %s"
                cursor.execute(sql, (like_term,))
            else:
                sql = "SELECT * FROM smsapp_student WHERE first_name LIKE %s OR last_name LIKE %s"
                cursor.execute(sql, (like_term, like_term))
            return cursor.fetchall()
    except Exception as e:
        print(f"Error searching students: {e}")
        return []
    finally:
        connection.close()
