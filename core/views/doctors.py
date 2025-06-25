from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from core.models import Doctor
from core.forms import DoctorUserRegister, DoctorUserEdit
from .appointments import role_required

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def doctor_list(request):
    query = request.GET.get('q', '')
    doctors = Doctor.objects.select_related('user').all()
    if query:
        doctors = doctors.annotate(
            full_name=Concat('user__first_name', Value(' '), 'user__last_name', output_field=CharField())
        ).filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialty__name__icontains=query) |  # Cambia specialty__icontains por specialty__name__icontains
            Q(dni__icontains=query) |
            Q(full_name__icontains=query)
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
                    'specialty': doctor.specialty.name,  # Cambia esto
                    'specialty_id': doctor.specialty.id, # Opcional: agrega el ID si lo necesitas en JS
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
        return render(request, 'doctors/doctor_detail.html', {'doctor': doctor})
    return render(request, 'dashboard.html', {
        'fragment': 'doctors/doctor_detail.html',
        'doctor': doctor
    })


@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def doctors_by_specialty(request):
    specialty_id = request.GET.get('specialty_id')
    if specialty_id:
        doctors = Doctor.objects.filter(specialty_id=specialty_id).select_related('user', 'specialty')
    else:
        doctors = Doctor.objects.all().select_related('user', 'specialty')
    data = {
        'doctors': [
            {'id': d.id, 'name': f"Dr(a). {d.user.first_name} {d.user.last_name} ({d.specialty.name})"}
            for d in doctors
        ]
    }
    return JsonResponse(data)