# Student Management System

A beginner-friendly, clean, and responsive **Student Management System** designed for academic institutions to easily manage student records. Built using **HTML5, CSS3, JavaScript, Bootstrap 5, Python (Django + PyMySQL)**, and **MySQL Database**.

---

## 🔑 Quick Start Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

---

## ⚠️ Important Note

> This project uses **Django templates** (`{% %}`, `{{ }}`).
> You **MUST** use `python manage.py runserver` to run it.
> Do **NOT** use `python -m http.server` — it won't process Django templates and will show raw code on the page.

---

## 🚀 Main Commands (Run These in Order)

> 📋 Just **copy and paste** each command one by one. Nothing else needed.

---

### ✅ Step 1 — Install All Required Packages

```bash
pip install -r requirements.txt
```

**What it does:** Installs all three required packages at once:
- **Django 6.x** — the web framework that runs the server and templates
- **PyMySQL** — lets Django connect to your MySQL database
- **Pillow** — needed for student profile image uploads

> If you only want to install manually one by one:
> ```bash
> pip install "Django>=6.0,<7.0"
> pip install pymysql
> pip install pillow
> ```

---

### ✅ Step 2 — Auto-Find MySQL & Import the Database

> Make sure **MySQL / XAMPP / WAMP** is running first.

**Command 1 — Auto-find MySQL on this laptop:**
```powershell
$mysql = @("C:\Program Files\MySQL","C:\xampp\mysql\bin","C:\wamp64\bin\mysql","C:\Program Files (x86)\MySQL") | ForEach-Object { Get-ChildItem $_ -Recurse -Filter "mysql.exe" -ErrorAction SilentlyContinue } | Where-Object { $_.FullName -notlike "*Workbench*" } | Select-Object -First 1 -ExpandProperty FullName
```

**Command 2 — Import the database:**
```powershell
Get-Content "database\student_management.sql" | & $mysql -u root -proot
```

**What it does:**
- Command 1 — Searches all common MySQL install locations (MySQL, XAMPP, WAMP) and auto-finds `mysql.exe`. Works on **any Windows laptop**.
- Command 2 — Creates the database, tables, and default admin user.

---

### ✅ Step 3 — Apply Django Migrations

```bash
python manage.py migrate
```

**What it does:** Sets up Django's required tables in MySQL. Run once before starting the server.

---

### ✅ Step 4 — Start the Server

```bash
python manage.py runserver
```

**What it does:** Starts the app. Open your browser at **http://127.0.0.1:8000** and login with `admin` / `admin123`.

---

## 🔧 Extra Useful Commands

### Check Python & Django Version
```bash
python --version
python -m django --version
```
**What it does:** Verifies Python and Django are correctly installed. Helpful for debugging version-related issues.

---

### Check for Project Errors
```bash
python manage.py check
```
**What it does:** Scans the project for configuration errors, missing settings, or broken URLs — without starting the server.

---

### Create a Django Superuser
```bash
python manage.py createsuperuser
```
**What it does:** Creates an admin account for Django's built-in admin panel at `http://127.0.0.1:8000/admin/`.

---

### Open Django Shell
```bash
python manage.py shell
```
**What it does:** Opens an interactive Python console where you can query the database and test code with full Django context loaded.

---

### Collect Static Files (Production Only)
```bash
python manage.py collectstatic
```
**What it does:** Gathers all CSS, JS, and image files into one folder for deployment on a production server. Not needed for local development.

---

## 🔁 Backup / Alternative Commands

> Use these only if the **main commands above don't work**.

---

### Backup for Step 1 — Install Packages

```bash
# If pip doesn't work, try pip3
pip3 install -r requirements.txt

# Install inside a virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Install each package manually
pip install "Django>=6.0,<7.0"
pip install pymysql==1.1.1
pip install pillow
```

---

### Backup for Step 2 — Import Database

```bash
# Option A — MySQL CLI (if mysql is in PATH)
mysql -u root -p < database/student_management.sql

# Option B — Create DB first, then import
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS student_management_db;"
mysql -u root -p student_management_db < database/student_management.sql

# Option C — Inside MySQL shell
mysql -u root -p
SOURCE database/student_management.sql;

# Option D — phpMyAdmin (GUI)
# Open http://localhost/phpmyadmin → Import → select database/student_management.sql
```

---

### Backup for Step 3 — Migrations

```bash
# See all pending migrations (without applying)
python manage.py showmigrations

# Create new migrations after changing models
python manage.py makemigrations

# Migrate only a specific app
python manage.py migrate smsapp
```

---

### Backup for Step 4 — Run Server

```bash
# Run on a different port (if 8000 is busy)
python manage.py runserver 8080

# Run on all network interfaces (share with other devices on WiFi)
python manage.py runserver 0.0.0.0:8000

# Check if port 8000 is already in use (Windows)
netstat -ano | findstr :8000
```

---

## ❌ Common Mistakes & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| Template shows `{% if %}` raw text | Used `python -m http.server` | Use `python manage.py runserver` instead |
| `mysql` not recognized | MySQL not in system PATH | Use full path: `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` |
| `No module named pymysql` | PyMySQL not installed | Run `pip install pymysql` |
| `Access denied for user root` | Wrong MySQL password | Update password in `student_management/settings.py` |
| Port 8000 already in use | Another server is running | Use `python manage.py runserver 8080` |

---

## 💡 How the System Works

This project has **3 layers** that work together:

```
Browser (HTML pages)
       ↓  user clicks a button / submits a form
Django (views.py) ← processes the request, talks to database
       ↓  reads/writes data
MySQL Database ← stores all student and admin records
```

**Example flow — Adding a student:**
1. User fills form on `add_student.html` and clicks Submit
2. Browser sends form data to Django
3. `views.py` → `add_student_view()` reads the data, validates it
4. View executes PyMySQL raw SQL: `INSERT INTO smsapp_student (...) VALUES (...)`
5. User is redirected to `view_students.html` with a success message

---

## 📁 Detailed File-by-File Explanation

---

### 🔵 Django App — `smsapp/`

This is the **heart of the project**. All backend logic lives here.

---

#### `smsapp/models.py` — Database Table Definition

Defines the **Student table** in MySQL. Each field becomes a column:

| Field | Type | Description |
|-------|------|-------------|
| `roll_number` | CharField | Unique ID for each student (e.g. `CS001`) |
| `first_name` | CharField | Student's first name |
| `last_name` | CharField | Student's last name |
| `gender` | CharField | `Male` or `Female` |
| `dob` | DateField | Date of Birth |
| `department` | CharField | e.g. `Computer Science` |
| `year` | CharField | e.g. `1st Year` |
| `semester` | CharField | e.g. `Semester 2` |
| `phone` | CharField | 10-digit phone number |
| `email` | EmailField | Student's email address |
| `address` | CharField | Student's home address |

---

#### `smsapp/views.py` — All Page Logic (Most Important File)

This file handles **what happens when you visit each page**. It has 9 functions:

**1. `login_view(request)`**
- URL: `/` (home page)
- If user is already logged in → redirect to dashboard
- If form submitted → check username & password using Django's `authenticate()`
- If correct → log in and redirect to dashboard
- If wrong → show error message `"Invalid Username or Password!"`

**2. `logout_view(request)`**
- URL: `/logout/`
- Logs out the current user and redirects to login page

**3. `dashboard_view(request)`**
- URL: `/dashboard/`
- Requires login (`@login_required`)
- Counts: total students, male students, female students, total departments
- Sends these numbers to `dashboard.html` to display as statistics

**4. `add_student_view(request)`**
- URL: `/add/`
- Requires login
- If form submitted → validates all fields:
  - All fields must be filled
  - Phone must be exactly 10 digits
  - Roll number must not already exist
- If valid → saves new student to MySQL
- Shows success or error message

**5. `view_students_view(request)`**
- URL: `/students/`
- Requires login
- Fetches all students from MySQL
- Sends the list to `view_students.html` to display in a table

**6. `update_student_view(request, id)`**
- URL: `/update/<id>/`
- Requires login
- Loads the student with the given `id` from MySQL
- If form submitted → validates and saves updated data
- Shows success or error message

**7. `delete_student_view(request, id)`**
- URL: `/delete/<id>/`
- Requires login
- Finds student by `id` and permanently deletes from MySQL
- Redirects to student list with success message

**8. `search_student_view(request)`**
- URL: `/search/`
- Requires login
- Reads `query` (search keyword) and `search_type` (`name`, `roll`, or `dept`) from URL
- Filters students using PyMySQL raw SQL with `LIKE %s`
- Sends filtered results to `search_student.html`

**9. `about_view` / `contact_view`**
- URLs: `/about/` and `/contact/`
- Just render the HTML pages — no database logic

---

#### `smsapp/urls.py` — URL Routing Table

Maps every URL to the correct view function:

| URL | View Function | Page |
|-----|--------------|------|
| `/` | `login_view` | Unified Login Page |
| `/logout/` | `logout_view` | Admin Logout |
| `/dashboard/` | `dashboard_view` | Admin Dashboard |
| `/add/` | `add_student_view` | Add Student |
| `/students/` | `view_students_view` | All Students List |
| `/student/<id>/` | `student_profile_view` | Student Profile |
| `/update/<id>/` | `update_student_view` | Edit Student |
| `/delete/<id>/` | `delete_student_view` | Delete Student |
| `/search/` | `search_student_view` | Search Students |
| `/fees/add/` | `add_fee_view` | Add Fee Payment |
| `/fees/` | `view_fees_view` | All Fee Records |
| `/fees/update/<id>/` | `update_fee_view` | Edit Fee Payment |
| `/fees/delete/<id>/` | `delete_fee_view` | Delete Fee Payment |
| `/fees/search/` | `search_fee_view` | Search Fee Records |
| `/fees/receipt/<id>/` | `fee_receipt_view` | Print Fee Receipt |
| `/attendance/add/` | `add_attendance_view` | Mark Attendance |
| `/attendance/` | `view_attendance_view` | View Attendance |
| `/marks/add/` | `add_marks_view` | Add Marks |
| `/departments/` | `departments_view` | Departments List |
| `/about/` | `about_view` | About Page |
| `/contact/` | `contact_view` | Contact Page |
| `/student/login/` | `student_login_view` | Student Login |
| `/student/register/` | `student_register_view` | Student Register |
| `/student/dashboard/` | `student_dashboard_view` | Student Dashboard |
| `/student/pay-fee/` | `student_pay_fee_view` | Student Pay Fee |
| `/student/logout/` | `student_logout_view` | Student Logout |

---

### 🔵 Django Settings — `student_management/`

#### `settings.py` — Project Configuration
- **INSTALLED_APPS** — Lists `smsapp` so Django knows about it
- **DATABASES** — Connects to MySQL with these settings:
  - Host: `localhost`, Port: `3306`
  - Database: `student_management_db`
  - User: `root`, Password: `root`
- **TEMPLATES → DIRS** — Tells Django to look for HTML files in the root folder

#### `urls.py` — Main URL Entry Point
- Connects the main project to `smsapp/urls.py`
- Also enables Django admin panel at `/admin/`

---

### 🔵 Backend Helper Files — `backend/`

> These are **standalone Python helper scripts** (not used by Django directly).
> They are an alternative way to connect to MySQL using raw PyMySQL.

#### `backend/db.py` — Database Connection
```python
def get_connection():
    # Connects to MySQL and returns a connection object
    # Uses: host=localhost, user=root, password='', db=student_management_db
```
- Called by all other backend files
- Returns `None` if connection fails and prints the error

#### `backend/auth.py` — Login Verification
```python
def verify_admin_login(username, password):
    # Runs: SELECT * FROM admins WHERE username=? AND password=?
    # Returns True if match found, False if not
```
- Checks the `admins` table directly using SQL

#### `backend/student.py` — Student CRUD Operations
```python
def add_student(...)       # INSERT a new student into MySQL
def get_all_students()     # SELECT all students from MySQL
def update_student(...)    # UPDATE an existing student record
def delete_student(id)     # DELETE a student by ID
```
- These are **standalone raw SQL helper functions** using PyMySQL directly
- The main app logic in `smsapp/views.py` also uses PyMySQL raw SQL (no Django ORM)
- These can be used independently to test database queries without Django

#### `backend/search.py` — Search Logic
```python
def search_students(search_by, keyword):
    # Filters students by name, roll number, or department
    # Uses LIKE %keyword% SQL query via PyMySQL
```

#### `backend/utils.py` — Dashboard Stats
```python
def calculate_dashboard_stats():
    # Returns: total_students, total_depts, total_fees, total_attendance
    # Queries smsapp_student and smsapp_feepayment tables directly
```

---

### 🔵 HTML Pages — Frontend Templates

#### `index.html` / `login.html` — Login Page
- Shows a login form with Username and Password fields
- Uses Django template tag `{% if error_msg %}` to show login errors
- On submit → sends `POST` request to Django's `login_view`

#### `dashboard.html` — Admin Dashboard
- Shows 4 stat cards: Total Students, Male, Female, Total Departments
- Uses `{{ total_students }}`, `{{ male_students }}` etc. (passed from `dashboard_view`)
- Has quick-action buttons: Add Student, View Students, Search

#### `add_student.html` — Add Student Form
- Form with all student fields: Roll No, Name, Gender, DOB, Department, Year, Semester, Phone, Email, Address
- Shows `{% if messages %}` Django messages for success/error
- Submits as `POST` to `/add/`

#### `view_students.html` — Student List Table
- Uses `{% for student in students %}` loop to display all students
- Each row has **Edit** and **Delete** buttons
- Edit button goes to `/update/<id>/`
- Delete button goes to `/delete/<id>/`

#### `update_student.html` — Edit Student Form
- Same as Add form but pre-filled with existing student data
- Uses `{{ student.first_name }}` etc. to pre-populate fields
- Submits as `POST` to `/update/<id>/`

#### `search_student.html` — Search Page
- Has a search bar and a dropdown to choose: Search by Name / Roll No / Department
- Submits as `GET` request to `/search/?query=...&search_type=...`
- Results shown in a table below using `{% for student in students %}`

#### `about.html` — About Page
- Static page with project info and developer details

#### `contact.html` — Contact Page
- Static contact form page

---

### 🔵 Database — `database/student_management.sql`

This SQL file creates everything needed:

```sql
-- Creates the database
CREATE DATABASE student_management_db;

-- Creates admins table (stores login credentials)
CREATE TABLE admins (
    username VARCHAR(50),
    password VARCHAR(255)
);

-- Creates students table (stores all student data)
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20) UNIQUE,
    first_name, last_name, gender, dob,
    department, year, semester,
    phone, email, address
);

-- Inserts default admin user
INSERT INTO admins VALUES ('admin', 'admin123');
```

---

### 🔵 Other Files

#### `manage.py` — Django Management Tool
- Entry point for all Django commands
- Do not edit this file
- Used to run: `migrate`, `runserver`, `createsuperuser`, `shell`, etc.

#### `.gitignore`
- Tells Git which files to NOT upload (e.g. `__pycache__`, `.env`, `db.sqlite3`)

#### `docs/database_design.md`
- Contains detailed ER diagram notes and database design documentation

---

## 🛠️ Project Structure

```text
Student_Management_System/
│
├── index.html              ← Login page (Django template)
├── login.html              ← Alternate login page
├── dashboard.html          ← Shows student stats
├── add_student.html        ← Add new student form
├── view_students.html      ← Table of all students
├── update_student.html     ← Edit student form
├── search_student.html     ← Search/filter students
├── about.html              ← About page
├── contact.html            ← Contact page
│
├── database/
│   └── student_management.sql  ← Creates DB + tables + admin user
│
├── backend/                ← Standalone PyMySQL helper scripts
│   ├── db.py               ← MySQL connection function
│   ├── auth.py             ← Login check with raw SQL
│   ├── student.py          ← CRUD function stubs
│   ├── search.py           ← Search function stub
│   └── utils.py            ← Stats function stub
│
├── smsapp/                 ← Main Django app (all live logic)
│   ├── models.py           ← Student table definition
│   ├── views.py            ← All page logic (9 functions)
│   ├── urls.py             ← URL → view mapping
│   └── migrations/         ← Auto-generated DB migration files
│
├── student_management/     ← Django project config
│   ├── settings.py         ← DB config, installed apps
│   ├── urls.py             ← Root URL config
│   └── wsgi.py             ← Production server entry
│
├── manage.py               ← Django CLI tool
├── docs/
│   └── database_design.md  ← ER diagram & DB design notes
├── .gitignore
└── README.md
```

---

## 📄 License & Credits
Built for educational purposes as a beginner-friendly capstone project. Free to use and modify!

