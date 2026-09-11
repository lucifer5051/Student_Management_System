import pymysql

def get_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='student_management_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None
