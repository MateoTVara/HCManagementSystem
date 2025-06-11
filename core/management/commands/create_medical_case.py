from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import *
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Crea un caso médico de ejemplo en el sistema'

    def handle(self, *args, **kwargs):
        # 1. Crear usuario médico
        medico_user = User.objects.create(
            username="jperez",
            first_name="Juan",
            last_name="Pérez Rodríguez",
            email="j.perez@clinicaperu.pe",
            role="DOCTOR",
            password=make_password("Zmkm_0104")
        )
        
        # 2. Crear perfil de médico
        doctor = Doctor.objects.create(
            user=medico_user,
            specialty="CARDIOLOGY",
            dni="48563217",
            gender="M"
        )
        
        # 3. Crear alergia
        alergia_penicilina = Allergy.objects.create(
            name="Penicilina",
            common_reactions="Urticaria, dificultad respiratoria, edema"
        )
        
        # 4. Crear paciente
        paciente = Patient.objects.create(
            dni="73451206",
            first_name="María",
            last_name="García López",
            date_of_birth="1985-07-15",
            gender="F",
            blood_type="A+",
            phone="+51987654321",
            address="Av. Arequipa 1230, Lima",
            email="maria.garcia@mail.com"
        )
        
        # 5. Asignar alergia al paciente
        PatientAllergy.objects.create(
            patient=paciente,
            allergy=alergia_penicilina,
            severity="grave",
            patient_reactions="Shock anafiláctico confirmado en 2022"
        )
        
        # 6. Historial médico
        historial = MedicalRecord.objects.create(
            patient=paciente,
            attending_doctor=doctor,
            additional_notes="Paciente con antecedentes familiares de cardiopatías",
            status="ACTIVE"
        )
        
        # 7. Cita médica
        cita = Appointment.objects.create(
            patient=paciente,
            doctor=doctor,
            medical_record=historial,
            date=datetime.now().date() + timedelta(days=2),
            time=datetime.strptime("14:30", "%H:%M").time(),
            reason="Control anual y dolor torácico ocasional",
            status="P"
        )
        
        # 8. Diagnóstico (usar enfermedad existente)
        enfermedad = Disease.objects.get(code_4='I10')  # Debe existir en tu DB
        Diagnosis.objects.create(
            appointment=cita,
            disease=enfermedad,
            notes="PA: 150/95 mmHg en dos tomas consecutivas",
            author=doctor
        )
        
        # 9. Medicamento
        medicamento = Medication.objects.create(
            name="Losartán Potásico",
            generic_name="Losartán",
            manufacturer="PharmaPerú SAC",
            dosage_form="TAB",
            strength="50 mg",
            quantity_in_stock=250
        )
        
        # 10. Receta médica
        Prescription.objects.create(
            appointment=cita,
            medication=medicamento,
            dosage="1 tableta",
            frequency="Una vez al día",
            duration="30 días",
            instructions="Tomar en ayunas, controlar presión semanal"
        )
        
        # 11. Contacto de emergencia
        EmergencyContact.objects.create(
            patient=paciente,
            full_name="Carlos García Torres",
            relationship="Esposo",
            phone="+51912345678",
            address="Av. Arequipa 1230, Lima"
        )
        
        # 12. Ingreso hospitalario
        Admission.objects.create(
            patient=paciente,
            admission_date=datetime.now() - timedelta(days=90),
            discharge_date=datetime.now() - timedelta(days=87),
            reason="Monitorización cardíaca por arritmia"
        )
        
        # 13. Examen médico
        MedicalExam.objects.create(
            appointment=cita,
            exam_type="ECG"
        )
        
        self.stdout.write(self.style.SUCCESS('Caso médico creado exitosamente!'))