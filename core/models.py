from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador del Sistema'),
        ('MANAGEMENT', 'Personal Administrativo'),
        ('DOCTOR', 'Médico'),
        ('ATTENDANT', 'Personal de Atención'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name="Rol",
        default='ADMIN'
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="core_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="core_user_permissions",
        related_query_name="user",
    )
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

class Doctor(models.Model):
    SPECIALTY_CHOICES = [
        ('CARDIOLOGY', 'Cardiología'),
        ('DERMATOLOGY', 'Dermatología'),
        ('NEUROLOGY', 'Neurología'),
        ('PEDIATRICS', 'Pediatría'),
        ('OTHER', 'Otra Especialidad'),
    ]

    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name="Usuario asociado"
    )
    specialty = models.CharField(
        max_length=50,
        choices=SPECIALTY_CHOICES,
        default='OTHER',
        verbose_name="Especialidad Médica"
    )

    dni = models.CharField(max_length=8, unique=True, verbose_name="DNI")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Género")
    
    def __str__(self):
        return f"Dr(a). {self.user.get_full_name()} ({self.get_specialty_display()})"
    
    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

class Allergy(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre de la alergia")
    common_reactions = models.TextField(verbose_name="Reacciones comunes")

    def __str__(self):
        return self.name


class Patient(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    dni = models.CharField(max_length=8, unique=True, verbose_name="DNI")
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    date_of_birth = models.DateField(verbose_name="Fecha de nacimiento")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Género")
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, verbose_name="Tipo de Sangre")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    email = models.EmailField(blank=True, verbose_name="Correo Electrónico")
    allergies = models.ManyToManyField(
        Allergy,
        through='PatientAllergy',
        blank=True,
        verbose_name="Alergias",
        help_text="Seleccione las alergias conocidas del paciente"
    )
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.dni}"
    
    def get_active_medical_record(self):
        return self.medicalrecord_set.filter(status='ACTIVE').first()
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]

class PatientAllergy(models.Model):
    SEVERITY_CHOICES = [
        ('leve', 'Leve'),
        ('moderada', 'Moderada'),
        ('grave', 'Grave'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    allergy = models.ForeignKey(Allergy, on_delete=models.CASCADE)
    severity = models.CharField(
        max_length=10, 
        choices=SEVERITY_CHOICES, 
        verbose_name="Severidad"
    )
    patient_reactions = models.TextField(verbose_name="Reacciones del paciente")
    date_registered = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Alergia del Paciente"
        verbose_name_plural = "Alergias de los Pacientes"
        unique_together = ('patient', 'allergy')

    def __str__(self):
        return f"{self.patient} - {self.allergy} ({self.severity})"

class MedicalRecord(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Activo'),
        ('CLOSED', 'Cerrado'),
        ('CHRONIC', 'Crónico'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    attending_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, verbose_name="Médico tratante")
    additional_notes = models.TextField(blank=True, verbose_name="Notas adicionales")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name="Estado del caso"
    )
    
    def __str__(self):
        return f"Registro de {self.patient} - {self.created_at.date()}"
    
    class Meta:
        verbose_name = "Historial Médico"
        verbose_name_plural = "Historiales Médicos"
        ordering = ['-created_at']

class Appointment(models.Model):
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE,
        verbose_name="Paciente",
    )
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE,
        verbose_name="Médico",
    )
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name="Caso médico asociado"
    )
    treatment = models.TextField(
        verbose_name="Tratamiento",
        blank=True
    )
    date = models.DateField(verbose_name="Fecha")
    time = models.TimeField(verbose_name="Hora")
    reason = models.TextField(
        verbose_name="Motivo de la cita",
        help_text="Describe el motivo de la cita médica."
    )
    
    STATUS_CHOICES = [
        ('P', 'Programada'),
        ('C', 'Completada'),
        ('N', 'No Presentado'),
        ('X', 'Cancelada'),
    ]
    status = models.CharField(
        max_length=1, 
        choices=STATUS_CHOICES, 
        default='P',
        verbose_name="Estado"
    )
    notes = models.TextField(blank=True, verbose_name="Notas posteriores a la cita")
    
    def __str__(self):
        return f"{self.patient} con {self.doctor} el {self.date} a las {self.time}"
    
    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['time']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date', 'time'],
                name='unique_doctor_timeslot',
                violation_error_message="El médico ya tiene una cita programada en este horario"
            ),
        ]

class Disease(models.Model):
    code_3 = models.CharField(max_length=4, verbose_name="Código CIE-10 (general)")
    code_4 = models.CharField(max_length=8, unique=True, verbose_name="Código CIE-10 (específico)")
    name = models.CharField(max_length=255, verbose_name="Nombre de la enfermedad")
    is_primary = models.BooleanField(default=False, verbose_name="Código principal (†)")
    is_manifestation = models.BooleanField(default=False, verbose_name="Código manifestación (*)")

    def save(self, *args, **kwargs):
        self.is_primary = '†' in self.code_4
        self.is_manifestation = '*' in self.code_4
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code_4} - {self.name}"

class Diagnosis(models.Model):
    appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.CASCADE,
        related_name='diagnoses',
        verbose_name="Cita asociada"
    )
    disease = models.ForeignKey(
        Disease,
        on_delete=models.PROTECT,
        verbose_name="Enfermedad"
    )
    notes = models.TextField(blank=True, verbose_name="Notas adicionales")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del diagnóstico")
    author = models.ForeignKey(
        'Doctor',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Médico que diagnosticó"
    )

    def __str__(self):
        return f"{self.disease} ({self.appointment})"

    class Meta:
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"
        ordering = ['-date']

class Medication(models.Model):
    DOSAGE_FORM_CHOICES = [
        ('TAB', 'Tableta'),
        ('CAP', 'Cápsula'),
        ('LIQ', 'Líquido'),
        ('INJ', 'Inyección'),
        ('CRE', 'Crema'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre del Medicamento")
    generic_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre Genérico")
    manufacturer = models.CharField(max_length=100, verbose_name="Fabricante")
    dosage_form = models.CharField(max_length=5, choices=DOSAGE_FORM_CHOICES, verbose_name="Forma Farmacéutica")
    strength = models.CharField(max_length=50, verbose_name="Concentración")
    quantity_in_stock = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Cantidad en Inventario")
    
    def __str__(self):
        return f"{self.name} ({self.strength} - {self.get_dosage_form_display()})"
    
    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"
        unique_together = ['name', 'manufacturer', 'dosage_form', 'strength']

class Prescription(models.Model):
    STATUS_CHOICES = [
        ('A', 'Activa'),
        ('C', 'Completada'),
        ('D', 'Cancelada'),
    ]
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name="Cita asociada"
    )
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, verbose_name="Medicamento")
    dosage = models.CharField(max_length=100, verbose_name="Dosis")
    frequency = models.CharField(max_length=100, verbose_name="Frecuencia")
    duration = models.CharField(max_length=50, verbose_name="Duración del Tratamiento")
    instructions = models.TextField(blank=True, verbose_name="Instrucciones Especiales")
     
    def __str__(self):
        return f"Receta de {self.medication} para {self.appointment.patient}"
    
    class Meta:
        verbose_name = "Receta Médica"
        verbose_name_plural = "Recetas Médicas"

class EmergencyContact(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    full_name = models.CharField(max_length=200, verbose_name="Nombre Completo")
    relationship = models.CharField(max_length=100, verbose_name="Parentesco")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    address = models.TextField(verbose_name="Dirección")
    
    def __str__(self):
        return f"Contacto de emergencia de {self.patient}: {self.full_name}"
    
    class Meta:
        verbose_name = "Contacto de Emergencia"
        verbose_name_plural = "Contactos de Emergencia"

class Admission(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    admission_date = models.DateTimeField(verbose_name="Fecha de Ingreso")
    discharge_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Alta")
    reason = models.TextField(verbose_name="Motivo de Ingreso")
    
    def __str__(self):
        return f"Ingreso de {self.patient} el {self.admission_date.date()}"
    
    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ['-admission_date']

class MedicalExam(models.Model):
    EXAM_TYPE_CHOICES = [
        ('BLOOD_TEST', 'Análisis de Sangre'),
        ('URINE_TEST', 'Análisis de Orina'),
        ('X_RAY', 'Radiografía'),
        ('MRI', 'Resonancia Magnética'),
        ('CT_SCAN', 'Tomografía Computarizada'),
        ('ULTRASOUND', 'Ultrasonido'),
        ('ECG', 'Electrocardiograma'),
        ('EEG', 'Electroencefalograma'),
        ('ENDOSCOPY', 'Endoscopia'),
        ('STOOL_TEST', 'Examen de Heces'),
        ('THROAT_SWAB', 'Cultivo de Garganta'),
        ('ALLERGY_TEST', 'Prueba de Alergia'),
        ('BIOPSY', 'Biopsia'),
        ('BONE_DENSITY', 'Densitometría Ósea'),
        ('MAMMOGRAM', 'Mamografía'),
        ('COLONOSCOPY', 'Colonoscopia'),
        ('ECHOCARDIOGRAM', 'Ecocardiograma'),
        ('PULMONARY_FUNCTION', 'Prueba de Función Pulmonar'),
        ('OTHER', 'Otro'),
    ]
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='medical_exams',
        verbose_name="Cita asociada"
    )
    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES,
        verbose_name="Tipo de Examen"
    )
    # result = models.TextField(verbose_name="Resultado")
    # notes = models.TextField(blank=True, verbose_name="Observaciones")
    # date_taken = models.DateField(verbose_name="Fecha de realización")
    # date_received = models.DateField(
    #     null=True,
    #     blank=True,
    #     verbose_name="Fecha de recepción de resultados"
    # )
    
    class Meta:
        verbose_name = "Examen Médico"
        verbose_name_plural = "Exámenes Médicos"

    def __str__(self):
        return f"{self.exam_type}"