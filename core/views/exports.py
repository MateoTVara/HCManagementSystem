from django.http import HttpResponse
from core.models import Patient, Doctor, Appointment
from .appointments import role_required
import requests

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def export_patients_excel(request):
    patients = Patient.objects.values(
        'dni', 'first_name', 'last_name', 'date_of_birth', 'gender', 'blood_type',
        'phone', 'address', 'email'
    )
    data = []
    for p in patients:
        p = dict(p)
        if p['date_of_birth']:
            p['date_of_birth'] = p['date_of_birth'].isoformat()
        data.append(p)
    java_service_url = 'http://localhost:8080/generate/patients/excel'
    response = requests.post(java_service_url, json=data)
    if response.status_code == 200:
        resp = HttpResponse(response.content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="pacientes.xlsx"'
        return resp
    return HttpResponse("Error generando el archivo", status=500)

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def export_doctors_excel(request):
    doctors = Doctor.objects.select_related('user').values(
        'dni',
        'user__first_name',
        'user__last_name',
        'user__email',
        'specialty',
        'gender'
    )
    data = []
    for d in doctors:
        data.append({
            "dni": d['dni'],
            "first_name": d['user__first_name'],
            "last_name": d['user__last_name'],
            "email": d['user__email'],
            "specialty": d['specialty'],
            "gender": str(d['gender']),
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
    appointments = Appointment.objects.select_related('patient', 'doctor__user')
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
            "notes": a.notes if a.notes else ""
        })
    java_service_url = 'http://localhost:8080/generate/appointments/excel'
    response = requests.post(java_service_url, json=data)
    if response.status_code == 200:
        resp = HttpResponse(response.content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="citas.xlsx"'
        return resp
    return HttpResponse("Error generando el archivo", status=500)