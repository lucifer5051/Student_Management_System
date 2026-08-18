from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add/', views.add_student_view, name='add_student'),
    path('students/', views.view_students_view, name='view_students'),
    path('student/<int:id>/', views.student_profile_view, name='student_profile'),
    path('update/<int:id>/', views.update_student_view, name='update_student'),
    path('delete/<int:id>/', views.delete_student_view, name='delete_student'),
    path('search/', views.search_student_view, name='search_student'),
    path('fees/add/', views.add_fee_view, name='add_fee'),
    path('fees/', views.view_fees_view, name='view_fees'),
    path('fees/update/<int:id>/', views.update_fee_view, name='update_fee'),
    path('fees/delete/<int:id>/', views.delete_fee_view, name='delete_fee'),
    path('fees/search/', views.search_fee_view, name='search_fee'),
    path('fees/receipt/<int:id>/', views.fee_receipt_view, name='fee_receipt'),
    path('attendance/add/', views.add_attendance_view, name='add_attendance'),
    path('attendance/', views.view_attendance_view, name='view_attendance'),
    path('marks/add/', views.add_marks_view, name='add_marks'),
    path('departments/', views.departments_view, name='departments'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # Student Portal Routes
    path('student/login/', views.student_login_view, name='student_login'),
    path('student/register/', views.student_register_view, name='student_register'),
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('student/pay-fee/', views.student_pay_fee_view, name='student_pay_fee'),
    path('student/logout/', views.student_logout_view, name='student_logout'),
]
