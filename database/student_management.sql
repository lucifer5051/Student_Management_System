-- =============================================================
-- Student Management System — Complete Database Schema & Seed Data
-- Database : student_management_db
-- Credentials: root / root
-- Django Version: 6.0.x
-- =============================================================

CREATE DATABASE IF NOT EXISTS student_management_db;
USE student_management_db;

-- ===========================================================
-- SECTION 1 — Educational Table (for Raw SQL Syllabus Modules)
-- ===========================================================

CREATE TABLE IF NOT EXISTS admins (
    admin_id  INT AUTO_INCREMENT PRIMARY KEY,
    username  VARCHAR(50)  NOT NULL UNIQUE,
    password  VARCHAR(50)  NOT NULL,
    full_name VARCHAR(100) NOT NULL
);

-- ===========================================================
-- SECTION 2 — Django System Tables
-- ===========================================================

CREATE TABLE IF NOT EXISTS django_content_type (
    id        INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model     VARCHAR(100) NOT NULL,
    UNIQUE KEY django_content_type_app_label_model_uniq (app_label, model)
);

CREATE TABLE IF NOT EXISTS auth_permission (
    id              INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename        VARCHAR(100) NOT NULL,
    UNIQUE KEY auth_permission_content_type_id_codename_uniq (content_type_id, codename),
    CONSTRAINT auth_permission_content_type_id_fk
        FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
);

CREATE TABLE IF NOT EXISTS auth_group (
    id   INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id            BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    group_id      INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_group_permissions_group_id_permission_id_uniq (group_id, permission_id),
    CONSTRAINT auth_group_permissions_group_id_fk
        FOREIGN KEY (group_id) REFERENCES auth_group (id),
    CONSTRAINT auth_group_permissions_permission_id_fk
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
);

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

CREATE TABLE IF NOT EXISTS auth_user_groups (
    id       BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id  INT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY auth_user_groups_user_id_group_id_uniq (user_id, group_id),
    CONSTRAINT auth_user_groups_user_id_fk  FOREIGN KEY (user_id)  REFERENCES auth_user (id),
    CONSTRAINT auth_user_groups_group_id_fk FOREIGN KEY (group_id) REFERENCES auth_group (id)
);

CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id            BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id       INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_user_user_permissions_user_id_permission_id_uniq (user_id, permission_id),
    CONSTRAINT auth_user_user_permissions_user_id_fk
        FOREIGN KEY (user_id) REFERENCES auth_user (id),
    CONSTRAINT auth_user_user_permissions_permission_id_fk
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
);

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

CREATE TABLE IF NOT EXISTS django_session (
    session_key  VARCHAR(40)  NOT NULL PRIMARY KEY,
    session_data LONGTEXT     NOT NULL,
    expire_date  DATETIME(6)  NOT NULL,
    KEY django_session_expire_date (expire_date)
);

CREATE TABLE IF NOT EXISTS django_migrations (
    id      BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    app     VARCHAR(255) NOT NULL,
    name    VARCHAR(255) NOT NULL,
    applied DATETIME(6)  NOT NULL
);

-- ===========================================================
-- SECTION 3 — Application Tables (smsapp)
-- ===========================================================

CREATE TABLE IF NOT EXISTS smsapp_student (
    id            BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    roll_number   VARCHAR(20)  NOT NULL UNIQUE,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    gender        VARCHAR(10)  NOT NULL,
    dob           DATE         NOT NULL,
    department    VARCHAR(50)  NOT NULL,
    year          VARCHAR(20)  NOT NULL,
    semester      VARCHAR(20)  NOT NULL,
    phone         VARCHAR(15)  NOT NULL,
    email         VARCHAR(100) NOT NULL,
    address       VARCHAR(255) NOT NULL,
    password      VARCHAR(50)  NOT NULL DEFAULT '123456',
    profile_image VARCHAR(100) NULL
);

CREATE TABLE IF NOT EXISTS smsapp_feepayment (
    id             BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    student_id     BIGINT        NOT NULL,
    amount         DECIMAL(10,2) NOT NULL,
    payment_date   DATE          NOT NULL,
    payment_method VARCHAR(30)   NOT NULL,
    status         VARCHAR(20)   NOT NULL,
    CONSTRAINT smsapp_feepayment_student_id_fk
        FOREIGN KEY (student_id) REFERENCES smsapp_student (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS smsapp_attendance (
    id              BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    student_id      BIGINT      NOT NULL,
    attendance_date DATE        NOT NULL,
    status          VARCHAR(10) NOT NULL,
    CONSTRAINT smsapp_attendance_student_id_fk
        FOREIGN KEY (student_id) REFERENCES smsapp_student (id) ON DELETE CASCADE
);

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
-- SECTION 4 — Seed Data
-- ===========================================================

-- 1. Educational admins table seed
INSERT IGNORE INTO admins (admin_id, username, password, full_name)
VALUES (1, 'admin', 'admin123', 'System Administrator');

-- 2. Django Content Types
INSERT IGNORE INTO django_content_type (id, app_label, model) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'group'),
(3, 'auth', 'permission'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(6, 'sessions', 'session'),
(7, 'smsapp', 'attendance'),
(8, 'smsapp', 'feepayment'),
(9, 'smsapp', 'mark'),
(10, 'smsapp', 'student');

-- 3. Django Migration Records (marks all existing migrations as applied)
INSERT IGNORE INTO django_migrations (id, app, name, applied) VALUES
(1, 'contenttypes', '0001_initial', NOW()),
(2, 'auth', '0001_initial', NOW()),
(3, 'admin', '0001_initial', NOW()),
(4, 'admin', '0002_logentry_remove_auto_add', NOW()),
(5, 'admin', '0003_logentry_add_action_flag_choices', NOW()),
(6, 'contenttypes', '0002_remove_content_type_name', NOW()),
(7, 'auth', '0002_alter_permission_name_max_length', NOW()),
(8, 'auth', '0003_alter_user_email_max_length', NOW()),
(9, 'auth', '0004_alter_user_username_opts', NOW()),
(10, 'auth', '0005_alter_user_last_login_null', NOW()),
(11, 'auth', '0006_require_contenttypes_0002', NOW()),
(12, 'auth', '0007_alter_validators_add_error_messages', NOW()),
(13, 'auth', '0008_alter_user_username_max_length', NOW()),
(14, 'auth', '0009_alter_user_last_name_max_length', NOW()),
(15, 'auth', '0010_alter_group_name_max_length', NOW()),
(16, 'auth', '0011_update_proxy_permissions', NOW()),
(17, 'auth', '0012_alter_user_first_name_max_length', NOW()),
(18, 'sessions', '0001_initial', NOW()),
(19, 'smsapp', '0001_initial', NOW()),
(20, 'smsapp', '0002_attendance_feepayment_mark', NOW()),
(21, 'smsapp', '0003_student_password_student_profile_image', NOW()),
(22, 'smsapp', '0004_auto_create_admin', NOW()),
(23, 'smsapp', '0005_alter_student_semester_alter_student_year', NOW());

-- 4. Default Django Admin Superuser (admin / admin123)
-- Genuine Django 6.0 PBKDF2-SHA256 password hash for 'admin123'
INSERT IGNORE INTO auth_user
    (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
VALUES
    (1,
     'pbkdf2_sha256$1200000$BAIvqVSZ12rm154PR5pZgt$JH0MrqatjM0kJ/hBEiHeWUnlg66jTlyDJiQqtDJ4ybs=',
     NULL, 1, 'admin', 'System', 'Administrator',
     'admin@example.com', 1, 1, NOW());

-- 5. Sample Students
INSERT IGNORE INTO smsapp_student
    (id, roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password)
VALUES
    (1, 'CS101', 'Rahul',  'Sharma', 'Male',   '2003-05-15',
     'Computer Engineering',   'Third Year',  'Semester 5',
     '9876543210', 'rahul.sharma@example.com',  'Flat 402, Green Valley, Mumbai', '123456'),
    (2, 'IT102', 'Priya',  'Patel',  'Female', '2004-02-20',
     'Information Technology',  'Second Year', 'Semester 3',
     '9812345678', 'priya.patel@example.com',   'B-12, Sagar Complex, Pune',     '123456');

-- 6. Sample Fee Payment
INSERT IGNORE INTO smsapp_feepayment
    (id, student_id, amount, payment_date, payment_method, status)
VALUES
    (1, 1, 45000.00, '2026-08-10', 'Net Banking', 'Paid');

-- 7. Sample Attendance
INSERT IGNORE INTO smsapp_attendance
    (id, student_id, attendance_date, status)
VALUES
    (1, 1, '2026-09-01', 'Present'),
    (2, 1, '2026-09-02', 'Present'),
    (3, 2, '2026-09-01', 'Present');

-- 8. Sample Marks
INSERT IGNORE INTO smsapp_mark
    (id, student_id, subject, marks_obtained, total_marks)
VALUES
    (1, 1, 'Database Management Systems', 88, 100),
    (2, 1, 'Operating Systems',           82, 100);
