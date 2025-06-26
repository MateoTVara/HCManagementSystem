from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from core.models import Appointment, MedicalRecord, Specialty  # Agrega Specialty
from core.forms import AppointmentRegister, AppointmentEdit
from django.db.models import Q, Count, Value, CharField
from django.db.models.functions import Concat
from datetime import date, datetime
import calendar
from django.shortcuts import get_object_or_404, render, redirect

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
                return render(request, 'appointments/appointment_register.html', {
                    'form': AppointmentRegister(),
                    'specialties': Specialty.objects.all()  # <-- Agrega esto
                })
            return redirect('dashboard')
    else:
        form = AppointmentRegister()

    # Siempre pasa specialties al contexto
    return render(request, 'appointments/appointment_register.html', {
        'form': form,
        'specialties': Specialty.objects.all()  # <-- Agrega esto
    })

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def appointment_list(request):
    query = request.GET.get('q', '').strip()
    date_str = request.GET.get('date', '').strip()
    appointments = Appointment.objects.all()

    # Filtrar por doctor si aplica
    if hasattr(request.user, 'doctor_profile'):
        appointments = appointments.filter(doctor=request.user.doctor_profile)

    # Filtrar por fecha si viene en GET
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            appointments = appointments.filter(date=date_obj)
        except ValueError:
            pass

    if query:
        appointments = appointments.annotate(
            patient_full_name=Concat('patient__first_name', Value(' '), 'patient__last_name', output_field=CharField()),
            doctor_full_name=Concat('doctor__user__first_name', Value(' '), 'doctor__user__last_name', output_field=CharField())
        ).filter(
            Q(patient__first_name__icontains=query) | 
            Q(patient__last_name__icontains=query) |
            Q(doctor__user__first_name__icontains=query) |
            Q(doctor__user__last_name__icontains=query) |
            Q(patient__dni__icontains=query) |
            Q(doctor__dni__icontains=query) |
            Q(patient_full_name__icontains=query) |
            Q(doctor_full_name__icontains=query)
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
    diagnoses = appointment.diagnoses.select_related('disease', 'author').all()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'appointments/appointment_detail.html', {
            'appointment': appointment,
            'diagnoses' : diagnoses,
        })

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'patient': appointment.patient,
        'doctor': appointment.doctor,
        'medical_record': appointment.medical_record,
        'prescriptions': appointment.prescriptions.all(),
        'exams': appointment.medical_exams.all(),
        'diagnoses': diagnoses,
    })

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def appointment_calendar(request):
    # Obtén mes y año de GET, o usa el actual
    try:
        current_month = int(request.GET.get('month', ''))
        current_year = int(request.GET.get('year', ''))
    except (TypeError, ValueError):
        today = date.today()
        current_year = today.year
        current_month = today.month

    # Filtrar por doctor si el usuario es doctor
    appointments_qs = Appointment.objects.filter(date__year=current_year, date__month=current_month)
    if hasattr(request.user, 'doctor_profile'):
        appointments_qs = appointments_qs.filter(doctor=request.user.doctor_profile)

    appointments = appointments_qs.values('date').annotate(total=Count('id'))
    appointments_dict = {appt['date'].isoformat(): appt['total'] for appt in appointments}

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(current_year, current_month)

    # Calcular mes anterior y siguiente
    prev_month = current_month - 1
    prev_year = current_year
    next_month = current_month + 1
    next_year = current_year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    if next_month > 12:
        next_month = 1
        next_year += 1

    current_date = date(current_year, current_month, 1)

    return render(request, 'appointments/appointment_calendar.html', {
        'month_days': month_days,
        'appointments_dict': appointments_dict,
        'current_month': date(current_year, current_month, 1).strftime('%B %Y'),
        'current_month_num': current_month,
        'weekday_headers': ['Dom','Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'current_year': current_year,
        'current_date': current_date,  # <-- Agrega esto
    })