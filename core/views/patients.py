from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from core.models import Patient, Allergy, PatientAllergy
from core.forms import PatientRegister, PatientEdit
from .appointments import role_required  # Usa el decorador ya definido

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
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
        patients = patients.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField())
        ).filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(dni__icontains=query) |
            Q(full_name__icontains=query)
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
    medical_records = patient.medicalrecord_set.select_related('attending_doctor__user').order_by('-created_at')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'patients/patient_detail.html', {
            'patient': patient,
            'medical_records': medical_records,
        })
    return render(request, 'dashboard.html', {
        'fragment': 'patients/patient_detail.html',
        'patient': patient,
        'medical_records': medical_records
    })