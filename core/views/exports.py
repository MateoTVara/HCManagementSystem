from django.http import HttpResponse
from core.models import Patient, PatientAllergy, EmergencyContact, Doctor, Appointment, Diagnosis
from .appointments import role_required
import requests
from core.models import MedicalRecord
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from datetime import datetime

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def export_patients_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    patients = Patient.objects.all()
    if start_date:
        patients = patients.filter(created_at__gte=start_date)
    if end_date:
        patients = patients.filter(created_at__lte=end_date)
    patients = patients.values(
        'id', 'dni', 'first_name', 'last_name', 'date_of_birth', 'gender', 'blood_type',
        'phone', 'address', 'email'
    )
    data = []
    for p in patients:
        p = dict(p)
        if p['date_of_birth']:
            p['date_of_birth'] = p['date_of_birth'].isoformat()
        # Alergias relacionadas
        allergies = PatientAllergy.objects.filter(patient_id=p['id']).select_related('allergy')
        p['allergies'] = [
            {
                "name": a.allergy.name,
                "severity": a.severity,
                "patient_reactions": a.patient_reactions
            }
            for a in allergies
        ]
        # Contactos de emergencia relacionados
        contacts = EmergencyContact.objects.filter(patient_id=p['id'])
        p['emergency_contacts'] = [
            {
                "full_name": c.full_name,
                "relationship": c.relationship,
                "phone": c.phone,
                "address": c.address
            }
            for c in contacts
        ]
        # Historiales médicos relacionados
        records = MedicalRecord.objects.filter(patient_id=p['id']).select_related('attending_doctor')
        p['medical_records'] = [
            {
                "created_at": r.created_at.isoformat() if r.created_at else "",
                "status": r.status,
                "attending_doctor": str(r.attending_doctor) if r.attending_doctor else "",
                "additional_notes": r.additional_notes,
            }
            for r in records
        ]
        data.append(p)
    # Elimina el campo 'id' antes de enviar
    for p in data:
        p.pop('id', None)
    java_service_url = 'http://localhost:8080/generate/patients/excel'
    response = requests.post(java_service_url, json=data)
    if response.status_code == 200:
        resp = HttpResponse(response.content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="pacientes.xlsx"'
        return resp
    return HttpResponse("Error generando el archivo", status=500)

@role_required(['ADMIN', 'MANAGEMENT'])
def export_doctors_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    doctors = Doctor.objects.all()
    if start_date:
        doctors = doctors.filter(user__date_joined__gte=start_date)
    if end_date:
        doctors = doctors.filter(user__date_joined__lte=end_date)
    doctors = doctors.select_related('user').values(
        'id',
        'dni',
        'user__first_name',
        'user__last_name',
        'user__email',
        'specialty',
        'gender'
    )
    data = []
    for d in doctors:
        # Historiales médicos asociados a este doctor
        medical_records = MedicalRecord.objects.filter(attending_doctor_id=d['id']).select_related('patient')
        records_data = [
            {
                "created_at": mr.created_at.isoformat() if mr.created_at else "",
                "status": mr.status,
                "patient_name": f"{mr.patient.first_name} {mr.patient.last_name}",
                "patient_dni": mr.patient.dni,
                "additional_notes": mr.additional_notes,
            }
            for mr in medical_records
        ]
        data.append({
            "dni": d['dni'],
            "first_name": d['user__first_name'],
            "last_name": d['user__last_name'],
            "email": d['user__email'],
            "specialty": d['specialty'],
            "gender": str(d['gender']),
            "medical_records": records_data,
        })
    java_service_url = 'http://localhost:8080/generate/doctors/excel'
    response = requests.post(java_service_url, json=data)
    if response.status_code == 200:
        resp = HttpResponse(response.content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="doctores.xlsx"'
        return resp
    return HttpResponse("Error generando el archivo", status=500)

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def export_appointments_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    appointments = Appointment.objects.all()
    if start_date:
        appointments = appointments.filter(date__gte=start_date)
    if end_date:
        appointments = appointments.filter(date__lte=end_date)
    # ... resto del código para exportar ...
    data = []
    for a in appointments:
        data.append({
            "date": a.date.isoformat() if a.date else "",
            "time": str(a.time) if a.time else "",
            "status": a.status,
            "reason": a.reason,
            "patient_first_name": a.patient.first_name,
            "patient_last_name": a.patient.last_name,
            "patient_dni": a.patient.dni,
            "doctor_first_name": a.doctor.user.first_name,
            "doctor_last_name": a.doctor.user.last_name,
            "doctor_dni": a.doctor.dni,
            "treatment": a.treatment if a.treatment else "",
            "notes": a.notes if a.notes else "",
            "diagnoses": [
                {"code_4": d.disease.code_4, "name": d.disease.name, "notes": d.notes}
                for d in a.diagnoses.all()
            ],
            "prescriptions": [
                {"medication": str(p.medication), "dosage": p.dosage, "instructions": p.instructions}
                for p in a.prescriptions.all()
            ],
            "exams": [
                {"exam_type": e.get_exam_type_display()}
                for e in a.medical_exams.all()
            ]
        })
    java_service_url = 'http://localhost:8080/generate/appointments/excel'
    response = requests.post(java_service_url, json=data)
    if response.status_code == 200:
        resp = HttpResponse(response.content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="citas.xlsx"'
        return resp
    return HttpResponse("Error generando el archivo", status=500)

@login_required
@user_passes_test(lambda u: u.role in ['ADMIN', 'MANAGEMENT'])
def export_top_diseases_pdf(request):
    diseases = Diagnosis.get_top_diseases()
    # Cambia la URL por la de tu servicio Java real
    JAVA_SERVICE_URL = "http://localhost:8080/generate/diseases/pdf"
    response = requests.post(JAVA_SERVICE_URL, json=diseases)
    if response.status_code == 200:
        pdf_bytes = response.content
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="enfermedades_frecuentes.pdf"'
        return resp
    else:
        return HttpResponse("Error generando el PDF", status=500)

@login_required
@user_passes_test(lambda u: u.role in ['ADMIN', 'MANAGEMENT'])
def reports_window(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, "reports/reports_window.html")
    return render(request, "dashboard.html", {
        "fragment": "reports/reports_window.html"
    })