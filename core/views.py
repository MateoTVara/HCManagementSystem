from functools import wraps
from django.http import HttpResponseForbidden
from core.models import *
from .forms import *
from django.db.models import Q, Count
from datetime import date
import calendar
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required, login_required

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
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'appointments/appointment_register.html', {'form': AppointmentRegister()})
            return redirect('dashboard')
        else:
            pass
    else:
        form = AppointmentRegister()

    template = 'appointments/appointment_register.html' if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else None
    
    return render(request, template, {'form': form})

def appointment_list(request):
    query = request.GET.get('q', '')
    appointments = Appointment.objects.all()
    
    if query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=query) | 
            Q(patient__last_name__icontains=query) |
            Q(doctor__user__first_name__icontains=query) |
            Q(doctor__user__last_name__icontains=query)
        )
            
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})

def appointment_remove(request, pk):
    if request.method == 'POST':
        appointment = Appointment.objects.get(pk=pk)
        appointment.delete()
    return redirect('appointment_list')

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

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR'])
def patient_register(request):
    allergies = Allergy.objects.all()  # Obtener todas las alergias
    
    if request.method == 'POST':
        form = PatientRegister(request.POST)
        if form.is_valid():
            patient = form.save()
            
            # Procesar alergias
            for allergy in allergies:
                if form.cleaned_data.get(f'allergy_{allergy.id}'):
                    PatientAllergy.objects.create(
                        patient=patient,
                        allergy=allergy,
                        severity=form.cleaned_data[f'severity_{allergy.id}'],
                        patient_reactions=form.cleaned_data[f'reactions_{allergy.id}']
                    )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'patients/patient_register.html', {'form': PatientRegister()})
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
            Q(last_name__icontains=query)
        )
    
    return render(request, 'patients/patient_list.html', {'patients': patients})

@role_required(['ADMIN', 'MANAGEMENT'])
def patient_remove(request, pk):
    if request.method == 'POST':
        patient = Patient.objects.get(pk=pk)
        patient.delete()
    return redirect('patient_list')

@role_required(['ADMIN', 'MANAGEMENT','ATTENDANT'])
def doctor_list(request):
    query = request.GET.get('q', '')
    doctors = Doctor.objects.select_related('user').all()
    
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialty__icontains=query)  # Cambio clave aquí
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