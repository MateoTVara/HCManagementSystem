from django.urls import reverse
from django.test import TestCase
from .models import *
from datetime import date, time

# =================
# Pruebas Unitarias
# ==================

class PatientModelTest(TestCase):
    def test_str_representation(self):
        patient = Patient.objects.create(
            first_name="Paciente",
            last_name="Prueba",
            dni="12345678",
            date_of_birth=date(2000, 1, 1),
            gender="M"
        )
        self.assertEqual(str(patient), "Paciente Prueba 12345678")

    def test_get_active_medical_record(self):
        patient = Patient.objects.create(
            first_name="Paciente",
            last_name="Activo",
            dni="87654321",
            date_of_birth=date(1990, 5, 5),
            gender="F"
        )
        record = MedicalRecord.objects.create(
            patient=patient,
            status='ACTIVE'
        )
        self.assertEqual(patient.get_active_medical_record(), record)

    def test_patient_str_includes_dni(self):
        patient = Patient.objects.create(
            first_name="Ana",
            last_name="García",
            dni="55554444",
            date_of_birth=date(1995, 7, 15),
            gender="F"
        )
        self.assertIn("55554444", str(patient))

    def test_emergency_contact_str(self):
        patient = Patient.objects.create(
            first_name="Carlos",
            last_name="Lopez",
            dni="99887766",
            date_of_birth=date(1985, 3, 10),
            gender="M"
        )
        contact = EmergencyContact.objects.create(
            patient=patient,
            full_name="María Lopez",
            relationship="Hermana",
            phone="123456789",
            address="Av. Siempre Viva 742"
        )
        self.assertIn("María Lopez", str(contact))
        self.assertIn("Carlos", str(contact))

class DoctorModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='doctor1',
            password='testpass',
            first_name='Juan',
            last_name='Pérez',
            role='DOCTOR'
        )

    def test_doctor_str(self):
        doctor = Doctor.objects.create(
            user=self.user,
            specialty='CARDIOLOGY',
            dni='12345679',
            gender='M'
        )
        self.assertIn('Juan Pérez', str(doctor))
        self.assertIn('Cardiología', str(doctor))

class AllergyModelTest(TestCase):
    def test_allergy_str(self):
        allergy = Allergy.objects.create(
            name="Polen",
            common_reactions="Estornudos, picazón"
        )
        self.assertEqual(str(allergy), "Polen")

class MedicalRecordModelTest(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            first_name="Mario",
            last_name="Sánchez",
            dni="10101010",
            date_of_birth=date(1980, 6, 15),
            gender="M"
        )
        self.doctor_user = User.objects.create_user(
            username='docuser',
            password='pass',
            first_name='Doc',
            last_name='Tor',
            role='DOCTOR'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty='CARDIOLOGY',
            dni='20202020',
            gender='M'
        )

    def test_medical_record_str(self):
        record = MedicalRecord.objects.create(
            patient=self.patient,
            attending_doctor=self.doctor,
            status='ACTIVE'
        )
        self.assertIn("Mario Sánchez", str(record))
        self.assertIn(str(record.created_at.date()), str(record))

class DiseaseModelTest(TestCase):
    def test_disease_str_and_flags(self):
        disease = Disease.objects.create(
            code_3="A00",
            code_4="A00.0†",
            name="Cólera",
        )
        self.assertIn("A00.0", str(disease))
        self.assertTrue(disease.is_primary)
        self.assertFalse(disease.is_manifestation)

# ======================
# Pruebas de Integración
# ======================

class PatientViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='hc_admin',
            password='Zmkm_0104',
            role='ADMIN'
        )
        self.client.login(username='hc_admin', password='Zmkm_0104')

    def test_patient_register_view_get(self):
        response = self.client.get(reverse('patient_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'patients/patient_register.html')

    def test_patient_register_view_post(self):
        response = self.client.post(reverse('patient_register'), {
            'first_name': 'Nuevo',
            'last_name': 'Paciente',
            'dni': '11223344',
            'date_of_birth': '2001-01-01',
            'gender': 'M',
            'emergency_full_name': 'Contacto Prueba',
            'emergency_relationship': 'Padre',
            'emergency_phone': '999999999',
            'emergency_address': 'Calle Falsa 123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Patient.objects.filter(dni='11223344').exists())

    def test_patient_list_view(self):
        # Crear pacientes de prueba
        Patient.objects.create(
            first_name="Pedro",
            last_name="Martinez",
            dni="22334455",
            date_of_birth=date(1992, 2, 2),
            gender="M"
        )
        Patient.objects.create(
            first_name="Lucía",
            last_name="Fernandez",
            dni="33445566",
            date_of_birth=date(1998, 8, 8),
            gender="F"
        )
        response = self.client.get(reverse('patient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pedro")
        self.assertContains(response, "Lucía")

    def test_patient_remove_view(self):
        patient = Patient.objects.create(
            first_name="Eliminar",
            last_name="Paciente",
            dni="44556677",
            date_of_birth=date(1990, 12, 12),
            gender="M"
        )
        # Eliminar paciente vía POST
        response = self.client.post(reverse('patient_remove', args=[patient.pk]))
        self.assertRedirects(response, reverse('patient_list'))
        self.assertFalse(Patient.objects.filter(pk=patient.pk).exists())

class DoctorViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            role='ADMIN'
        )
        self.client.login(username='admin', password='adminpass')
        self.user = User.objects.create_user(
            username='doctor2',
            password='testpass',
            first_name='Laura',
            last_name='Gómez',
            role='DOCTOR'
        )
        Doctor.objects.create(
            user=self.user,
            specialty='DERMATOLOGY',
            dni='87654321',
            gender='F'
        )

    def test_doctor_list_view(self):
        response = self.client.get(reverse('doctor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laura")
        self.assertContains(response, "Dermatología")

class AllergyViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin2',
            password='adminpass2',
            role='ADMIN'
        )
        self.client.login(username='admin2', password='adminpass2')

    def test_allergy_register_view_post(self):
        response = self.client.post(reverse('allergy_register'), {
            'name': 'Ácaros',
            'common_reactions': 'Picazón, estornudos'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Allergy.objects.filter(name='Ácaros').exists())

class AppointmentViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin3',
            password='adminpass3',
            role='ADMIN'
        )
        self.client.login(username='admin3', password='adminpass3')
        self.patient = Patient.objects.create(
            first_name="Cita",
            last_name="Paciente",
            dni="55556666",
            date_of_birth=date(1999, 9, 9),
            gender="F"
        )
        self.doctor_user = User.objects.create_user(
            username='doctor3',
            password='testpass3',
            first_name='Rosa',
            last_name='Mora',
            role='DOCTOR'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty='PEDIATRICS',
            dni='33334444',
            gender='F'
        )

    def test_appointment_register_view_post(self):
        response = self.client.post(reverse('appointment_register'), {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'date': '2025-01-01',
            'time': '10:00',
            'reason': 'Chequeo general'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Appointment.objects.filter(patient=self.patient, doctor=self.doctor).exists())

    def test_appointment_list_view(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=date(2025, 1, 1),
            time=time(10, 0),
            reason="Chequeo general",
            status='P'
        )
        response = self.client.get(reverse('appointment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cita Paciente")  # Nombre del paciente
        self.assertContains(response, "Rosa Mora")      # Nombre del doctor