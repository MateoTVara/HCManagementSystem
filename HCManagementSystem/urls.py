"""
Configuración de URLs para el proyecto HCManagementSystem.

La lista `urlpatterns` enruta las URLs a las vistas correspondientes.
Para más información, consulta:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Ejemplos:
Vistas basadas en funciones
    1. Agrega un import:  from my_app import views
    2. Agrega una URL:  path('', views.home, name='home')
Vistas basadas en clases
    1. Agrega un import:  from other_app.views import Home
    2. Agrega una URL:  path('', Home.as_view(), name='home')
Incluyendo otra configuración de URLs
    1. Importa la función include: from django.urls import include, path
    2. Agrega una URL:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de autenticación
    path('', views.login_view, name='login'),  # Vista de inicio de sesión
    path('logout/', views.logout_view, name='logout'),  # Vista de cierre de sesión
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  # Panel principal
    path('profile/', views.user_profile, name='user_profile'),

    # Rutas para la gestión de citas
    path('appointment/register/', views.appointment_register, name='appointment_register'),  # Registrar cita
    path('appointment/list/', views.appointment_list, name='appointment_list'),  # Listar citas
    path('appointment/remove/<int:pk>/', views.appointment_remove, name='appointment_remove'),  # Eliminar cita
    path('appointment/calendar/', views.appointment_calendar, name='appointment_calendar'),  # Calendario de citas
    path('appointment/edit/<int:pk>/', views.appointment_edit, name='appointment_edit'),  # Editar cita
    path('appointment/detail/<int:pk>/', views.appointment_detail, name='appointment_detail'),  # Detalle de cita

    # Rutas para la gestión de pacientes
    path('patient/list/', views.patient_list, name='patient_list'),  # Listar pacientes
    path('patient/register/', views.patient_register, name='patient_register'),  # Registrar paciente
    path('patient/remove/<int:pk>/', views.patient_remove, name='patient_remove'),  # Eliminar paciente
    path('patient/edit/<int:pk>/', views.patient_edit, name='patient_edit'),  # Editar paciente
    path('patient/detail/<int:pk>/', views.patient_detail, name='patient_detail'),  # Detalle de paciente

    # Rutas para la gestión de doctores
    path('doctor/list/', views.doctor_list, name='doctor_list'),  # Listar doctores
    path('doctor/remove/<int:pk>/', views.doctor_remove, name='doctor_remove'),  # Eliminar doctor
    path('doctor/edit/<int:pk>/', views.doctor_edit, name='doctor_edit'),  # Editar doctor
    path('doctor/register/', views.doctor_register, name='doctor_register'),  # Registrar doctor
    path('doctor/detail/<int:pk>/', views.doctor_detail, name='doctor_detail'),  # Detalle de doctor

    # Rutas para la gestión de historial médico
    path('medicalrecord/<int:pk>/update/', views.medicalrecord_update, name='medicalrecord_update'),
    path('medicalrecord/detail/<int:pk>/', views.medicalrecord_detail, name='medicalrecord_detail'),

    # Rutas para la gestión de alergias
    path('allergy/register/', views.allergy_register, name='allergy_register'),  # Registrar alergia
    path('allergy/partial_list/', views.allergy_list_partial, name='allergy_list_partial'),  # Listar alergias (parcial)
    path('allergy/partial_list/<int:patient_id>/', views.allergy_list_partial_patient, name='allergy_list_partial_patient'),  # Listar alergias por paciente

    # Rutas para la exportación de datos
    path('reports/', views.reports_window, name='reports_window'),
    path('export/patients/excel/', views.export_patients_excel, name='export_patients_excel'),
    path('export/doctors/excel/', views.export_doctors_excel, name='export_doctors_excel'),
    path('export/appointments/excel/', views.export_appointments_excel, name='export_appointments_excel'),
    path('export/diseases/pdf/', views.export_top_diseases_pdf, name='export_top_diseases_pdf'),

    # Consultas de doctor
    path('consultation/list/', views.consultation_list, name='consultation_list'),
    path('consultation/start/<int:pk>/', views.consultation_start, name='consultation_start'),
    path('consultation/<int:appointment_id>/prescription/register/', views.prescription_register, name='prescription_register'),
    path('consultation/<int:appointment_id>/exam/register/', views.exam_register, name='exam_register'),
    path('consultation/diagnosis/delete/<int:pk>/', views.diagnosis_delete, name='diagnosis_delete'),
    path('consultation/prescription/delete/<int:pk>/', views.prescription_delete, name='prescription_delete'),
    path('consultation/exam/delete/<int:pk>/', views.exam_delete, name='exam_delete'),

    path('ajax/disease-search/', views.disease_search, name='disease_search'),
]
