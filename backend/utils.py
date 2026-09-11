import pymysql
try:
    from .db import get_connection
except ImportError:
    from db import get_connection

def calculate_dashboard_stats():
    connection = get_connection()
    if not connection:
        return {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_students FROM smsapp_student")
            total_students = cursor.fetchone().get('total_students', 0)
            
            cursor.execute("SELECT COUNT(DISTINCT department) AS total_depts FROM smsapp_student")
            total_depts = cursor.fetchone().get('total_depts', 0)
            
            cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total_fees FROM smsapp_feepayment WHERE status='Paid'")
            total_fees = cursor.fetchone().get('total_fees', 0)
            
            cursor.execute("SELECT COUNT(*) AS total_attendance FROM smsapp_attendance")
            total_attendance = cursor.fetchone().get('total_attendance', 0)
            
            return {
                'total_students': total_students,
                'total_depts': total_depts,
                'total_fees': total_fees,
                'total_attendance': total_attendance
            }
    except Exception as e:
        print(f"Error calculating stats: {e}")
        return {}
    finally:
        connection.close()
