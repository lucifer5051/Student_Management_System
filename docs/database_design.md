# Database Design Document - Student Management System

This version only uses the concepts you've learned in your syllabus.

---

## 1. Introduction to Database Design

A database is an organized collection of structured information or data. 
In our Student Management System, we use **MySQL** as our Relational Database Management System (RDBMS) and **PyMySQL** to connect our Python backend with MySQL.

---

## 2. Fundamental Database Concepts Explained

### Primary Key
- **Definition**: A Primary Key is a special column in a database table that uniquely identifies each record/row.
- **Why it is needed**: No two students can have the exact same Student ID or Roll Number. The Primary Key prevents duplicate records.
- **Example in our system**: `student_id` in the `students` table and `admin_id` in the `admins` table.

### Foreign Key
- **Definition**: A Foreign Key is a column in one table that links to the Primary Key of another table.
- **Why it is used in real applications**: It links related data across multiple tables (for example, linking a student record to a specific department table).
- **In our syllabus version**: To keep our database simple and beginner-friendly, we store the department name directly in the `students` table as text, but understanding Foreign Keys is essential for your theoretical exams!

---

## 3. Database Normalization (Step-by-Step)

Normalization is the process of organizing data in a database to reduce data redundancy (duplication) and improve data integrity.

### First Normal Form (1NF)
- **Rule**: Each field must contain atomic (indivisible) values, and there must be no repeating groups.
- **How our design satisfies 1NF**:
  - We separated `name` into `first_name` and `last_name`.
  - Every column holds a single value (e.g., one phone number, one email).

### Second Normal Form (2NF)
- **Rule**: Table must be in 1NF, and all non-key attributes must be fully dependent on the Primary Key.
- **How our design satisfies 2NF**:
  - Every detail (First Name, Roll Number, Department, Email) depends directly on the unique `student_id`.

### Third Normal Form (3NF)
- **Rule**: Table must be in 2NF, and there should be no transitive dependencies (non-key columns depending on other non-key columns).
- **How our design satisfies 3NF**:
  - All attributes belong strictly to the student entity identified by `student_id`.

---

## 4. Text-Based ER Diagram (Entity-Relationship)

```text
+-------------------------------------------------------+
|                       ADMINS                          |
+-------------------------------------------------------+
| admin_id (PK) : INT AUTO_INCREMENT                   |
| username       : VARCHAR(50) UNIQUE                   |
| password       : VARCHAR(50)                          |
| full_name      : VARCHAR(100)                         |
+-------------------------------------------------------+

+-------------------------------------------------------+
|                      STUDENTS                         |
+-------------------------------------------------------+
| student_id (PK): INT AUTO_INCREMENT                   |
| roll_number    : VARCHAR(20) UNIQUE                   |
| first_name     : VARCHAR(50)                          |
| last_name      : VARCHAR(50)                          |
| gender         : VARCHAR(10)                          |
| dob            : DATE                                 |
| department     : VARCHAR(50)                          |
| year           : VARCHAR(10)                          |
| semester       : VARCHAR(10)                          |
| phone          : VARCHAR(15)                          |
| email          : VARCHAR(100)                         |
| address        : VARCHAR(255)                         |
+-------------------------------------------------------+
```

---

## 5. Table Data Dictionary

### Table 1: `admins`
Stores login credentials for administrators.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `admin_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for admin |
| `username` | VARCHAR(50) | NOT NULL, UNIQUE | Admin username for login |
| `password` | VARCHAR(50) | NOT NULL | Admin password for authentication |
| `full_name` | VARCHAR(100) | NOT NULL | Full name of the administrator |

### Table 2: `students`
Stores complete details of registered students.

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `student_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique system-generated student ID |
| `roll_number` | VARCHAR(20) | NOT NULL, UNIQUE | College Roll Number |
| `first_name` | VARCHAR(50) | NOT NULL | Student's First Name |
| `last_name` | VARCHAR(50) | NOT NULL | Student's Last Name |
| `gender` | VARCHAR(10) | NOT NULL | Gender (Male/Female/Other) |
| `dob` | DATE | NOT NULL | Date of Birth (YYYY-MM-DD) |
| `department` | VARCHAR(50) | NOT NULL | Department Name (e.g. AI & ML) |
| `year` | VARCHAR(10) | NOT NULL | Academic Year (e.g. FY, SY, TY) |
| `semester` | VARCHAR(10) | NOT NULL | Current Semester (e.g. Sem 1, Sem 2) |
| `phone` | VARCHAR(15) | NOT NULL | Contact Phone Number |
| `email` | VARCHAR(100) | NOT NULL | Email Address |
| `address` | VARCHAR(255) | NOT NULL | Residential Address |
