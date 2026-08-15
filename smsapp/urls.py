from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add/', views.add_student_view, name='add_student'),
    path('students/', views.view_students_view, name='view_students'),
    path('update/<int:id>/', views.update_student_view, name='update_student'),
    path('delete/<int:id>/', views.delete_student_view, name='delete_student'),
    path('search/', views.search_student_view, name='search_student'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
