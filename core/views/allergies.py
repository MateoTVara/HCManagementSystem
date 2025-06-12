from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from core.models import Allergy, PatientAllergy, Patient
from core.forms import AllergyRegister
from .appointments import role_required
import requests

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