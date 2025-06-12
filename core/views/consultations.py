from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import render_to_string
from core.models import Appointment, Diagnosis, Disease, MedicalRecord, Medication, MedicalExam, Prescription
from .appointments import role_required
from datetime import datetime, timedelta
from django.db.models import Q

@role_required(['DOCTOR'])
def consultation_list(request):
    doctor = request.user.doctor_profile
    now = timezone.localtime()

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
        if now > appt_datetime + timedelta(minutes=15):
            appt.status = 'N'
            appt.save(update_fields=['status'])

    appointments = Appointment.objects.filter(
        doctor=doctor,
        date__gte=now.date(),
        status='P'
    ).order_by('date', 'time')

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
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        treatment = request.POST.get('treatment', '')
        mr_status = request.POST.get('mr_status')
        mr_notes = request.POST.get('mr_notes', '')

        disease_id = request.POST.get('disease')
        diagnosis_notes = request.POST.get('diagnosis_notes', '')

        medical_record = appointment.medical_record
        if medical_record:
            if mr_status in dict(MedicalRecord.STATUS_CHOICES):
                medical_record.status = mr_status
            medical_record.additional_notes = mr_notes
            medical_record.save(update_fields=['status', 'additional_notes'])

        appointment.notes = notes
        appointment.treatment = treatment
        appointment.status = 'C'
        appointment.save(update_fields=['notes', 'treatment', 'status'])

        if disease_id:
            disease = Disease.objects.filter(pk=disease_id).first()
            if disease:
                if not Diagnosis.objects.filter(appointment=appointment, disease=disease, author=request.user.doctor_profile).exists():
                    Diagnosis.objects.create(
                        appointment=appointment,
                        disease=disease,
                        notes=diagnosis_notes,
                        author=request.user.doctor_profile
                    )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            diagnosis_html = render_to_string(
                "consultations/partials/diagnosis_list.html",
                {"diagnoses": appointment.diagnoses.all()}
            )
            return JsonResponse({'success': True, 'diagnosis_html': diagnosis_html})
        return redirect('consultation_list')

    medications = Medication.objects.all()
    exam_type_choices = MedicalExam.EXAM_TYPE_CHOICES
    diseases = Disease.objects.all().order_by('name')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'consultations/consultation_window.html', {
            'appointment': appointment,
            'medications': medications,
            'exam_type_choices': exam_type_choices,
            'diseases': diseases,
        })
    return render(request, 'dashboard.html', {
        'fragment': 'consultations/consultation_window.html',
        'appointment': appointment,
        'medications': medications,
        'diseases': diseases,
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
        html = render_to_string(
            "consultations/partials/prescription_list.html",
            {"prescriptions": appointment.prescriptions.all()}
        )
        return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

@require_POST
@role_required(['DOCTOR'])
def prescription_delete(request, pk):
    pres = get_object_or_404(Prescription, pk=pk)
    appointment = pres.appointment
    pres.delete()
    html = render_to_string("consultations/partials/prescription_list.html", {"prescriptions": appointment.prescriptions.all()})
    return JsonResponse({'success': True, 'html': html})

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

@require_POST
@role_required(['DOCTOR'])
def exam_delete(request, pk):
    exam = get_object_or_404(MedicalExam, pk=pk)
    appointment = exam.appointment
    exam.delete()
    html = render_to_string("consultations/partials/exam_list.html", {"exams": appointment.medical_exams.all()})
    return JsonResponse({'success': True, 'html': html})

@require_POST
@role_required(['DOCTOR'])
def medicalrecord_update(request, pk):
    medical_record = get_object_or_404(MedicalRecord, pk=pk)
    status = request.POST.get('status')
    notes = request.POST.get('additional_notes', '')
    if status not in dict(MedicalRecord.STATUS_CHOICES):
        return JsonResponse({'success': False, 'error': 'Estado inválido.'}, status=400)
    medical_record.status = status
    medical_record.additional_notes = notes
    medical_record.save(update_fields=['status', 'additional_notes'])
    return JsonResponse({
        'success': True,
        'status_display': medical_record.get_status_display(),
        'notes': medical_record.additional_notes
    })

@role_required(['ADMIN', 'MANAGEMENT', 'DOCTOR', 'ATTENDANT'])
def medicalrecord_detail(request, pk):
    medical_record = get_object_or_404(MedicalRecord, pk=pk)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'medical_records/medical_record_detail.html', {
            'medical_record': medical_record,
        })
    return render(request, 'dashboard.html', {
        'fragment': 'medical_records/medical_record_detail.html',
        'medical_record': medical_record,
    })

def disease_search(request):
    q = request.GET.get('q', '')
    results = []
    if q:
        diseases = Disease.objects.filter(
            Q(name__icontains=q) | Q(code_4__icontains=q)
        ).order_by('name')[:20]
        results = [
            {'id': d.id, 'text': d.code_4, 'desc': d.name}
            for d in diseases
        ]
    return JsonResponse({'results': results})

@require_POST
@role_required(['DOCTOR'])
def diagnosis_delete(request, pk):
    diag = get_object_or_404(Diagnosis, pk=pk)
    appointment = diag.appointment
    diag.delete()
    html = render_to_string("consultations/partials/diagnosis_list.html", {"diagnoses": appointment.diagnoses.all()})
    return JsonResponse({'success': True, 'diagnosis_html': html})