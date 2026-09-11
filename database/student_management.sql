-- ==========================================================
-- Student Management System — Complete Database Schema
-- Database : student_management_db
-- Credentials: root / root
-- Django Version: 6.0.x
-- Run ONCE before: python manage.py migrate
-- ==========================================================

CREATE DATABASE IF NOT EXISTS student_management_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE student_management_db;

-- ===========================================================
-- SECTION 1 — Django System Tables
-- (These are also created by: python manage.py migrate)
-- ===========================================================

-- Django: contenttypes
CREATE TABLE IF NOT EXISTS django_content_type (
    id          INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    app_label   VARCHAR(100) NOT NULL,
    model       VARCHAR(100) NOT NULL,
    UNIQUE KEY django_content_type_app_label_model (app_label, model)
);

-- Django: auth permissions
CREATE TABLE IF NOT EXISTS auth_permission (
    id              INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename        VARCHAR(100) NOT NULL,
    UNIQUE KEY auth_permission_content_type_id_codename (content_type_id, codename),
    CONSTRAINT auth_permission_content_type_id_fk
        FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
);

-- Django: auth groups
CREATE TABLE IF NOT EXISTS auth_group (
    id   INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- Django: auth group permissions (many-to-many)
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id            BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    group_id      INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_group_permissions_group_id_permission_id (group_id, permission_id),
    CONSTRAINT auth_group_permissions_group_id_fk
        FOREIGN KEY (group_id) REFERENCES auth_group (id),
    CONSTRAINT auth_group_permissions_permission_id_fk
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
);

-- Django: auth users (admin accounts)
CREATE TABLE IF NOT EXISTS auth_user (
    id           INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    password     VARCHAR(128) NOT NULL,
    last_login   DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username     VARCHAR(150) NOT NULL UNIQUE,
    first_name   VARCHAR(150) NOT NULL DEFAULT '',
    last_name    VARCHAR(150) NOT NULL DEFAULT '',
    email        VARCHAR(254) NOT NULL DEFAULT '',
    is_staff     TINYINT(1) NOT NULL DEFAULT 0,
    is_active    TINYINT(1) NOT NULL DEFAULT 1,
    date_joined  DATETIME(6) NOT NULL
);

-- Django: auth user groups (many-to-many)
CREATE TABLE IF NOT EXISTS auth_user_groups (
    id       BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id  INT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY auth_user_groups_user_id_group_id (user_id, group_id),
    CONSTRAINT auth_user_groups_user_id_fk  FOREIGN KEY (user_id)  REFERENCES auth_user (id),
    CONSTRAINT auth_user_groups_group_id_fk FOREIGN KEY (group_id) REFERENCES auth_group (id)
);

-- Django: auth user permissions (many-to-many)
CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id            BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id       INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_user_user_permissions_user_id_permission_id (user_id, permission_id),
    CONSTRAINT auth_user_user_permissions_user_id_fk
        FOREIGN KEY (user_id) REFERENCES auth_user (id),
    CONSTRAINT auth_user_user_permissions_permission_id_fk
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
);

-- Django: admin log
CREATE TABLE IF NOT EXISTS django_admin_log (
    id              INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    action_time     DATETIME(6) NOT NULL,
    object_id       LONGTEXT NULL,
    object_repr     VARCHAR(200) NOT NULL,
    action_flag     SMALLINT UNSIGNED NOT NULL,
    change_message  LONGTEXT NOT NULL,
    content_type_id INT NULL,
    user_id         INT NOT NULL,
    CONSTRAINT django_admin_log_content_type_id_fk
        FOREIGN KEY (content_type_id) REFERENCES django_content_type (id),
    CONSTRAINT django_admin_log_user_id_fk
        FOREIGN KEY (user_id) REFERENCES auth_user (id)
);

-- Django: sessions
CREATE TABLE IF NOT EXISTS django_session (
    session_key  VARCHAR(40)  NOT NULL PRIMARY KEY,
    session_data LONGTEXT     NOT NULL,
    expire_date  DATETIME(6)  NOT NULL
);
CREATE INDEX IF NOT EXISTS django_session_expire_date ON django_session (expire_date);

-- Django: migrations tracker
CREATE TABLE IF NOT EXISTS django_migrations (
    id      BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    app     VARCHAR(255) NOT NULL,
    name    VARCHAR(255) NOT NULL,
    applied DATETIME(6) NOT NULL
);

-- ===========================================================
-- SECTION 2 — Application Tables (smsapp)
-- These match Django models in smsapp/models.py exactly.
-- ===========================================================

-- Students Table  (smsapp/models.py → class Student)
CREATE TABLE IF NOT EXISTS smsapp_student (
    id           BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    roll_number  VARCHAR(20)  NOT NULL UNIQUE,
    first_name   VARCHAR(50)  NOT NULL,
    last_name    VARCHAR(50)  NOT NULL,
    gender       VARCHAR(10)  NOT NULL,
    dob          DATE         NOT NULL,
    department   VARCHAR(50)  NOT NULL,
    year         VARCHAR(20)  NOT NULL,
    semester     VARCHAR(20)  NOT NULL,
    phone        VARCHAR(15)  NOT NULL,
    email        VARCHAR(100) NOT NULL,
    address      VARCHAR(255) NOT NULL,
    password     VARCHAR(50)  NOT NULL DEFAULT '123456',
    profile_image VARCHAR(100) NULL
);

-- Fee Payments Table  (smsapp/models.py → class FeePayment)
CREATE TABLE IF NOT EXISTS smsapp_feepayment (
    id             BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    student_id     BIGINT       NOT NULL,
    amount         DECIMAL(10,2) NOT NULL,
    payment_date   DATE         NOT NULL,
    payment_method VARCHAR(30)  NOT NULL,
    status         VARCHAR(20)  NOT NULL,
    CONSTRAINT smsapp_feepayment_student_id_fk
        FOREIGN KEY (student_id) REFERENCES smsapp_student (id) ON DELETE CASCADE
);

-- Attendance Table  (smsapp/models.py → class Attendance)
CREATE TABLE IF NOT EXISTS smsapp_attendance (
    id              BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    student_id      BIGINT NOT NULL,
    attendance_date DATE   NOT NULL,
    status          VARCHAR(10) NOT NULL,
    CONSTRAINT smsapp_attendance_student_id_fk
        FOREIGN KEY (student_id) REFERENCES smsapp_student (id) ON DELETE CASCADE
);

-- Marks Table  (smsapp/models.py → class Mark)
CREATE TABLE IF NOT EXISTS smsapp_mark (
    id             BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    student_id     BIGINT      NOT NULL,
    subject        VARCHAR(50) NOT NULL,
    marks_obtained INT         NOT NULL,
    total_marks    INT         NOT NULL,
    CONSTRAINT smsapp_mark_student_id_fk
        FOREIGN KEY (student_id) REFERENCES smsapp_student (id) ON DELETE CASCADE
);

-- ===========================================================
-- SECTION 3 — Seed Data
-- ===========================================================

-- Default admin user for Django login (admin / admin123)
-- Password hash = pbkdf2_sha256 of "admin123"
INSERT IGNORE INTO auth_user
    (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
VALUES
    (1,
     'pbkdf2_sha256$870000$default$admin123hash',
     NULL, 1, 'admin', 'System', 'Administrator',
     'admin@example.com', 1, 1, NOW());

-- NOTE: The password hash above is a placeholder.
-- The real hash is automatically set when you run:
--   python manage.py migrate
-- Django's migration 0004_auto_create_admin.py sets the correct hash.
-- You do NOT need to manually edit this password.

-- Sample Students
INSERT IGNORE INTO smsapp_student
    (id, roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password)
VALUES
    (1, 'CS101', 'Rahul',  'Sharma', 'Male',   '2003-05-15',
     'Computer Engineering',   'Third Year',  'Semester 5',
     '9876543210', 'rahul.sharma@example.com',  'Flat 402, Green Valley, Mumbai', '123456'),
    (2, 'IT102', 'Priya',  'Patel',  'Female', '2004-02-20',
     'Information Technology',  'Second Year', 'Semester 3',
     '9812345678', 'priya.patel@example.com',   'B-12, Sagar Complex, Pune',     '123456');

-- Sample Fee Payment
INSERT IGNORE INTO smsapp_feepayment
    (id, student_id, amount, payment_date, payment_method, status)
VALUES
    (1, 1, 45000.00, '2026-08-10', 'Net Banking', 'Paid');

-- Sample Attendance
INSERT IGNORE INTO smsapp_attendance
    (id, student_id, attendance_date, status)
VALUES
    (1, 1, '2026-09-01', 'Present'),
    (2, 1, '2026-09-02', 'Present'),
    (3, 2, '2026-09-01', 'Present');

-- Sample Marks
INSERT IGNORE INTO smsapp_mark
    (id, student_id, subject, marks_obtained, total_marks)
VALUES
    (1, 1, 'Database Management Systems', 88, 100),
    (2, 1, 'Operating Systems',           82, 100);
