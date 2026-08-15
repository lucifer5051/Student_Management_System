from db import get_connection

def verify_admin_login(username, password):
    connection = get_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM admins WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()
            if result:
                return True
            else:
                return False
    except Exception as e:
        print(f"Database Query Error: {e}")
        return False
    finally:
        connection.close()
