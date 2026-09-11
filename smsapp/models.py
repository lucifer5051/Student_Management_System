from django.db import models

class Student(models.Model):
    roll_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    department = models.CharField(max_length=50)
    year = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=255)
    password = models.CharField(max_length=50, default='123456')
    profile_image = models.ImageField(upload_to='student_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=30)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.student.first_name} - {self.amount}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.student.first_name} - {self.attendance_date}"


class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    marks_obtained = models.IntegerField()
    total_marks = models.IntegerField()

    def __str__(self):
        return f"{self.student.first_name} - {self.subject}"
