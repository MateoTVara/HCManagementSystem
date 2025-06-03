from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from core.models import *
from .forms import *
from django.db.models import Q, Count
from datetime import date, datetime, timedelta
import calendar
from django.views.generic import View
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required, login_required
import requests
from django.http import HttpResponse
from django.template.loader import render_to_string

# Create your views here.

@login_not_required
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')  
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect(next_url if next_url else 'dashboard')
        
        return render(request, 'login.html', {
            'error': 'Credenciales inválidas',
            'next': next_url
        })
    
    return render(request, 'login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('login')


class DashboardView(View):
    def get(self, request):
        return render(request, 'dashboard.html')


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def appointment_register(request):
    if request.method == 'POST':
        form = AppointmentRegister(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            patient = appointment.patient
            doctor = appointment.doctor

            # Buscar historial médico activo
            medical_record = patient.get_active_medical_record()
            if not medical_record:
                medical_record = MedicalRecord.objects.create(
                    patient=patient,
                    attending_doctor=doctor,
                    status='ACTIVE'
                )
            appointment.medical_record = medical_record
            appointment.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'appointments/appointment_register.html', {'form': AppointmentRegister()})
            return redirect('dashboard')
        # Si el form no es válido, sigue abajo
    else:
        form = AppointmentRegister()

    template = 'appointments/appointment_register.html' if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else None
    return render(request, template, {'form': form})


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def appointment_list(request):
    query = request.GET.get('q', '')
    appointments = Appointment.objects.all()

    #Validación para doctores
    if hasattr(request.user, 'doctor_profile'):
        appointments = appointments.filter(doctor=request.user.doctor_profile)
    
    if query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=query) | 
            Q(patient__last_name__icontains=query) |
            Q(doctor__user__first_name__icontains=query) |
            Q(doctor__user__last_name__icontains=query)
        )
            
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})


@role_required(['ADMIN', 'MANAGEMENT', 'ATTENDANT'])
def appointment_remove(request, pk):
    if request.method == 'POST':
        appointment = Appointment.objects.get(pk=pk)
        appointment.delete()
    return redirect('appointment_list')


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def appointment_edit(request, pk):
    appointment = Appointment.objects.get(pk=pk)
    print("DEBUG fecha de la cita:", appointment.date, type(appointment.date)) 

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = AppointmentEdit(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save()
            data = {
                'success': True,
                'appointment': {
                    'id': appointment.id,
                    'date': appointment.date,
                    'time': appointment.time,
                    'patient': str(appointment.patient),
                    'doctor': str(appointment.doctor),
                    'status': appointment.status,
                }
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = AppointmentEdit(instance=appointment)
        return render(request, 'appointments/appointment_edit.html', {'form': form, 'appointment': appointment})

    if request.method == 'POST':
        form = AppointmentEdit(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AppointmentEdit(instance=appointment)

    return render(request, 'appointments/appointment_edit.html', {'form': form, 'appointment': appointment})


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Solo el fragmento para AJAX
        return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})
    # Si NO es AJAX, renderiza el dashboard y pasa el fragmento como variable
    return render(request, 'dashboard.html', {
        'fragment': 'appointments/appointment_detail.html',
        'appointment': appointment
    })


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def appointment_calendar(request):
    today = date.today()
    current_year = today.year
    current_month = today.month

    appointments = (Appointment.objects
                    .filter(date__year=current_year, date__month=current_month)
                    .values('date')
                    .annotate(total=Count('id')))
    
    appointments_dict = {appt['date'].isoformat(): appt['total'] for appt in appointments}

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(current_year, current_month)

    return render(request, 'appointments/appointment_calendar.html', {
        'month_days': month_days,
        'appointments_dict': appointments_dict,
        'current_month': today.strftime('%B %Y'),
        'current_month_num': today.month,
        'weekday_headers': ['Sun','Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    })


@role_required(['ADMIN', 'MANAGEMENT', 'ATTENDANT'])
def patient_register(request):
    allergies = Allergy.objects.all()
    
    if request.method == 'POST':
        form = PatientRegister(request.POST)
        if form.is_valid():
            patient = form.save()
            
            for allergy in allergies:
                if form.cleaned_data.get(f'allergy_{allergy.id}'):
                    PatientAllergy.objects.update_or_create(
                        patient=patient,
                        allergy=allergy,
                        defaults={
                            'severity': form.cleaned_data[f'severity_{allergy.id}'],
                            'patient_reactions': form.cleaned_data[f'reactions_{allergy.id}']
                        }
                    )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'patients/patient_register.html', {
                    'form': PatientRegister(),
                    'allergies': allergies,
                    'severity_choices': PatientAllergy.SEVERITY_CHOICES
                })
            return redirect('dashboard')
    else:
        form = PatientRegister()
    
    template = 'patients/patient_register.html' if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else None
    return render(request, template, {
        'form': form,
        'allergies': allergies,
        'severity_choices': PatientAllergy.SEVERITY_CHOICES
    })


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def patient_list(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all()
    
    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(dni__icontains=query)
        )
    
    return render(request, 'patients/patient_list.html', {'patients': patients})


@role_required(['ADMIN', 'MANAGEMENT'])
def patient_remove(request, pk):
    if request.method == 'POST':
        patient = Patient.objects.get(pk=pk)
        patient.delete()
    return redirect('patient_list')


@role_required(['ADMIN', 'MANAGEMENT', 'ATTENDANT'])
def patient_edit(request, pk):
    patient = Patient.objects.get(pk=pk)
    allergies = Allergy.objects.all()
    severity_choices = PatientAllergy.SEVERITY_CHOICES
    patient_allergy_ids = list(patient.allergies.values_list('id', flat=True))
    allergy_severity = {pa.allergy_id: pa.severity for pa in PatientAllergy.objects.filter(patient=patient)}
    allergy_reactions = {pa.allergy_id: pa.patient_reactions for pa in PatientAllergy.objects.filter(patient=patient)}

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            data = {
                'success': True,
                'patient': {
                    'id': patient.id,
                    'dni': patient.dni,
                    'first_name': patient.first_name,
                    'last_name': patient.last_name,
                    'date_of_birth': patient.date_of_birth.isoformat(),
                    'gender': patient.gender,
                    'blood_type': patient.blood_type,
                    'phone': patient.phone,
                    'address': patient.address,
                    'email': patient.email,
                }
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = PatientEdit(instance=patient)
        return render(request, 'patients/patient_edit.html', {
            'form': form,
            'patient': patient,
            'allergies': allergies,
            'severity_choices': severity_choices,
            'patient_allergy_ids': patient_allergy_ids,
            'allergy_severity': allergy_severity,
            'allergy_reactions': allergy_reactions,
        })

    if request.method == 'POST':
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PatientEdit(instance=patient)

    return render(request, 'patients/patient_edit.html', {
        'form': form,
        'patient': patient,
        'allergies': allergies,
        'severity_choices': severity_choices,
        'patient_allergy_ids': patient_allergy_ids,
        'allergy_severity': allergy_severity,
        'allergy_reactions': allergy_reactions,
    })


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = patient.appointment_set.select_related('doctor__user').order_by('-date', '-time')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Solo el fragmento para AJAX
        return render(request, 'patients/patient_detail.html', {
            'patient': patient,
            'appointments': appointments,
        })
    # Si NO es AJAX, renderiza el dashboard y pasa el fragmento como variable
    return render(request, 'dashboard.html', {
        'fragment': 'patients/patient_detail.html',
        'patient': patient,
        'appointments': appointments
    })


@role_required(['ADMIN', 'MANAGEMENT', 'ATTENDANT'])
def doctor_list(request):
    query = request.GET.get('q', '')
    doctors = Doctor.objects.select_related('user').all()
    
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialty__icontains=query)
        )
    
    return render(request, 'doctors/doctor_list.html', {
        'doctors': doctors,
        'search_query': query
    })


@role_required(['ADMIN', 'MANAGEMENT'])
def doctor_remove(request, pk):
    if request.method == 'POST':
        doctor = Doctor.objects.get(pk=pk)
        doctor.delete()
    return redirect('doctor_list')


@role_required(['ADMIN', 'MANAGEMENT'])
def doctor_register(request):
    if request.method == 'POST':
        form = DoctorUserRegister(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'doctors/doctor_register.html', {'form': DoctorUserRegister()})
            return redirect('doctor_list')
    else:
        form = DoctorUserRegister()
    template = 'doctors/doctor_register.html' if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else None
    return render(request, template, {'form': form})


@role_required(['ADMIN', 'MANAGEMENT'])
def doctor_edit(request, pk):
    doctor = Doctor.objects.get(pk=pk)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = DoctorUserEdit(request.POST, instance=doctor)
        if form.is_valid():
            doctor = form.save()
            data = {
                'success': True,
                'doctor': {
                    'id': doctor.id,
                    'first_name': doctor.user.first_name,
                    'last_name': doctor.user.last_name,
                    'email': doctor.user.email,
                    'specialty': doctor.specialty,
                    'dni': doctor.dni,
                    'gender': doctor.gender,
                }
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = DoctorUserEdit(instance=doctor)
        return render(request, 'doctors/doctor_edit.html', {'form': form, 'doctor': doctor})

    if request.method == 'POST':
        form = DoctorUserEdit(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = DoctorUserEdit(instance=doctor)

    return render(request, 'doctors/doctor_edit.html', {'form': form, 'doctor': doctor})


@role_required(['ADMIN', 'MANAGEMENT'])
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Solo el fragmento para AJAX
        return render(request, 'doctors/doctor_detail.html', {'doctor': doctor})
    # Si NO es AJAX, renderiza el dashboard y pasa el fragmento como variable
    return render(request, 'dashboard.html', {
        'fragment': 'doctors/doctor_detail.html',
        'doctor': doctor
    })


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def allergy_register(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = AllergyRegister(request.POST)
        if form.is_valid():
            allergy = form.save()
            data = {
                'success': True,
                'allergy': {
                    'id': allergy.id,
                    'name': allergy.name,
                }
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    if request.method == 'POST':
        form = AllergyRegister(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AllergyRegister()

    return render(request, 'allergies/allergy_register.html', {'form': form})


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def allergy_list_partial(request):
    allergies = Allergy.objects.all()
    severity_choices = PatientAllergy.SEVERITY_CHOICES
    return render(request, 'allergies/partials/allergy_list.html', {
        'allergies': allergies,
        'severity_choices': severity_choices
    })


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def allergy_list_partial_patient(request, patient_id):
    allergies = Allergy.objects.all()
    severity_choices = PatientAllergy.SEVERITY_CHOICES
    patient = Patient.objects.get(pk=patient_id)
    patient_allergy_ids = list(patient.allergies.values_list('id', flat=True))
    allergy_severity = {pa.allergy_id: pa.severity for pa in PatientAllergy.objects.filter(patient=patient)}
    allergy_reactions = {pa.allergy_id: pa.patient_reactions for pa in PatientAllergy.objects.filter(patient=patient)}
    return render(request, 'allergies/partials/allergy_list.html', {
        'allergies': allergies,
        'severity_choices': severity_choices,
        'patient_allergy_ids': patient_allergy_ids,
        'allergy_severity': allergy_severity,
        'allergy_reactions': allergy_reactions,
    })


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
        'specialty'
    )
    data = []
    for d in doctors:
        data.append({
            "dni": d['dni'],
            "first_name": d['user__first_name'],
            "last_name": d['user__last_name'],
            "email": d['user__email'],
            "specialty": d['specialty'],
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
    appointments = Appointment.objects.select_related('patient', 'doctor__user').values(
        'date', 'time', 'status', 'reason',
        'patient__first_name', 'patient__last_name', 'patient__dni',
        'doctor__user__first_name', 'doctor__user__last_name', 'doctor__dni'
    )
    data = []
    for a in appointments:
        data.append({
            "date": a['date'].isoformat() if a['date'] else "",
            "time": str(a['time']) if a['time'] else "",
            "status": a['status'],
            "reason": a['reason'],
            "patient_first_name": a['patient__first_name'],
            "patient_last_name": a['patient__last_name'],
            "patient_dni": a['patient__dni'],
            "doctor_first_name": a['doctor__user__first_name'],
            "doctor_last_name": a['doctor__user__last_name'],
            "doctor_dni": a['doctor__dni'],
        })
    java_service_url = 'http://localhost:8080/generate/appointments/excel'
    response = requests.post(java_service_url, json=data)
    if response.status_code == 200:
        resp = HttpResponse(response.content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="citas.xlsx"'
        return resp
    return HttpResponse("Error generando el archivo", status=500)


@role_required(['DOCTOR'])
def consultation_list(request):
    doctor = request.user.doctor_profile
    now = timezone.localtime()

    # Actualiza automáticamente citas "Programada" a "No presentado" si han pasado 15 minutos
    fifteen_minutes_ago = now - timedelta(minutes=15)
    expired_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='P',
        date__lte=now.date()
    )
    for appt in expired_appointments:
        appt_datetime = datetime.combine(appt.date, appt.time)
        appt_datetime = timezone.make_aware(appt_datetime, timezone.get_current_timezone())
        appt.time_until = appt_datetime - now
        print(f"Ahora: {now}, Cita: {appt_datetime}, Estado: {appt.status}, Limite: {appt_datetime + timedelta(minutes=15)}")
        if now > appt_datetime + timedelta(minutes=15):
            appt.status = 'N'
            appt.save(update_fields=['status'])

    appointments = Appointment.objects.filter(
        doctor=doctor,
        date__gte=now.date(),
        status= 'P'
    ).order_by('date', 'time')

    # Encuentra la cita más próxima futura o de hoy y hora >= ahora
    next_appointment = None
    for appt in appointments:
        appt_datetime = datetime.combine(appt.date, appt.time)
        appt_datetime = timezone.make_aware(appt_datetime)
        if appt_datetime.date() == now.date() and appt.status == 'P':
            if appt_datetime.time() <= now.time():
                next_appointment = appt
                break
            elif appt_datetime.time() > now.time():
                next_appointment = appt
                break
        elif appt_datetime > now and appt.status == 'P':
            next_appointment = appt
            break

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'consultations/consultation_list.html', {
            'appointments': appointments,
            'next_appointment': next_appointment,
            'now': now,
        })
    return render(request, 'dashboard.html', {
        'fragment': 'consultations/consultation_list.html',
        'appointments': appointments,
        'next_appointment': next_appointment,
        'now': now,
    })


@role_required(['DOCTOR'])
def consultation_start(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    medications = Medication.objects.all()
    exam_type_choices = MedicalExam.EXAM_TYPE_CHOICES

    if request.method == 'POST':
        # Guardar notas y marcar como completada
        notes = request.POST.get('notes', '')
        appointment.notes = notes
        appointment.status = 'C'  # Completada
        appointment.save(update_fields=['notes', 'status'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('consultation_list')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'consultations/consultation_window.html', {
            'appointment': appointment,
            'medications': medications,
            'exam_type_choices': exam_type_choices,
        })
    return render(request, 'dashboard.html', {
        'fragment': 'consultations/consultation_window.html',
        'appointment': appointment,
        'medications': medications,
    })


@role_required(['DOCTOR'])
def prescription_register(request, appointment_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        med_id = request.POST.get('medication')
        dosage = request.POST.get('dosage')
        frequency = request.POST.get('frequency')
        duration = request.POST.get('duration')
        instructions = request.POST.get('instructions', '')
        if not (med_id and dosage and frequency and duration):
            return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios.'}, status=400)
        try:
            medication = Medication.objects.get(pk=med_id)
        except Medication.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Medicamento inválido.'}, status=400)
        Prescription.objects.create(
            appointment=appointment,
            medication=medication,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
            instructions=instructions
        )
        # Renderiza el partial actualizado
        html = render_to_string(
            "consultations/partials/prescription_list.html",
            {"prescriptions": appointment.prescriptions.all()}
        )
        return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)


@role_required(['DOCTOR'])
def exam_register(request, appointment_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        exam_type = request.POST.get('exam_type')
        if not exam_type:
            return JsonResponse({'success': False, 'error': 'Debe seleccionar un tipo de examen.'}, status=400)
        MedicalExam.objects.create(
            appointment=appointment,
            exam_type=exam_type
        )
        html = render_to_string(
            "consultations/partials/exam_list.html",
            {"exams": appointment.medical_exams.all()}
        )
        return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)