"""
db.py — PyMySQL database helper for Student Management System
Provides:
  - get_connection() : opens a PyMySQL connection to student_management_db
  - R               : dot-accessible row wrapper so templates can use
                      record.field  OR  record.related.field
                      instead of record['field']
"""

import pymysql
import pymysql.cursors


# ---------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------

def get_connection():
    """Open and return a PyMySQL connection using DictCursor."""
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='student_management_db',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    return conn


# ---------------------------------------------------------------
# Row helper — converts a dict (SQL row) to a dot-accessible object
# ---------------------------------------------------------------

class R:
    """
    Wraps a dict so templates can do:
        {{ student.first_name }}   instead of  {{ student.first_name }}
    Also converts any nested dict values into R objects, so:
        {{ payment.student.first_name }}  works when student is a dict.
    """

    def __init__(self, data):
        if data is None:
            data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, R(value))
            else:
                setattr(self, key, value)

    def __repr__(self):
        return str(self.__dict__)

    def __bool__(self):
        return bool(self.__dict__)
