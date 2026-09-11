-- ==========================================================
-- Student Management System Database Script
-- Database: student_management_db
-- Credentials: root / root
-- ==========================================================

CREATE DATABASE IF NOT EXISTS student_management_db;
USE student_management_db;

-- 1. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    full_name VARCHAR(100) NOT NULL
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS smsapp_student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    dob DATE NOT NULL,
    department VARCHAR(50) NOT NULL,
    year VARCHAR(10) NOT NULL,
    semester VARCHAR(10) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    password VARCHAR(50) NOT NULL DEFAULT '123456',
    profile_image VARCHAR(100) NULL
);

-- 3. Fee Payments Table
CREATE TABLE IF NOT EXISTS smsapp_feepayment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES smsapp_student(id) ON DELETE CASCADE
);

-- 4. Attendance Table
CREATE TABLE IF NOT EXISTS smsapp_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status VARCHAR(10) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES smsapp_student(id) ON DELETE CASCADE
);

-- 5. Marks Table
CREATE TABLE IF NOT EXISTS smsapp_mark (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    marks_obtained INT NOT NULL,
    total_marks INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES smsapp_student(id) ON DELETE CASCADE
);

-- Seed Data: Sample Admin
INSERT IGNORE INTO admins (admin_id, username, password, full_name)
VALUES (1, 'admin', 'admin123', 'System Administrator');

-- Seed Data: Sample Students
INSERT IGNORE INTO smsapp_student (id, roll_number, first_name, last_name, gender, dob, department, year, semester, phone, email, address, password)
VALUES 
(1, 'CS101', 'Rahul', 'Sharma', 'Male', '2003-05-15', 'Computer Engineering', 'Third Year', 'Semester 5', '9876543210', 'rahul.sharma@example.com', 'Flat 402, Green Valley, Mumbai', '123456'),
(2, 'IT102', 'Priya', 'Patel', 'Female', '2004-02-20', 'Information Technology', 'Second Year', 'Semester 3', '9812345678', 'priya.patel@example.com', 'B-12, Sagar Complex, Pune', '123456');

-- Seed Data: Sample Fee Payments
INSERT IGNORE INTO smsapp_feepayment (id, student_id, amount, payment_date, payment_method, status)
VALUES 
(1, 1, 45000.00, '2026-08-10', 'Net Banking', 'Paid');

-- Seed Data: Sample Attendance
INSERT IGNORE INTO smsapp_attendance (id, student_id, attendance_date, status)
VALUES 
(1, 1, '2026-09-01', 'Present'),
(2, 1, '2026-09-02', 'Present'),
(3, 2, '2026-09-01', 'Present');

-- Seed Data: Sample Marks
INSERT IGNORE INTO smsapp_mark (id, student_id, subject, marks_obtained, total_marks)
VALUES 
(1, 1, 'Database Management Systems', 88, 100),
(2, 1, 'Operating Systems', 82, 100);
