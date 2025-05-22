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
        default='ATTENDANT'
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
    
    def __str__(self):
        return f"Dr(a). {self.user.get_full_name()} ({self.get_specialty_display()})"
    
    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

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

    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    date_of_birth = models.DateField(verbose_name="Fecha de nacimiento")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Género")
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, verbose_name="Tipo de Sangre")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    email = models.EmailField(blank=True, verbose_name="Correo Electrónico")
    allergies = models.TextField(
        blank=True,
        verbose_name="Alergias",
        help_text="Lista de alergias del paciente, incluyendo severidad y reacciones"
    )
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]

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

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    diagnosis = models.TextField(verbose_name="Diagnóstico")
    treatment = models.TextField(verbose_name="Tratamiento")
    attending_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, verbose_name="Médico tratante")
    additional_notes = models.TextField(blank=True, verbose_name="Notas adicionales")
    
    def __str__(self):
        return f"Registro de {self.patient} - {self.created_at.date()}"
    
    class Meta:
        verbose_name = "Historial Médico"
        verbose_name_plural = "Historiales Médicos"
        ordering = ['-created_at']

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
    expiration_date = models.DateField(verbose_name="Fecha de Caducidad")
    reorder_level = models.IntegerField(default=10, verbose_name="Nivel de Reorden")
    
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
    
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, verbose_name="Historial Médico")
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, verbose_name="Medicamento")
    dosage = models.CharField(max_length=100, verbose_name="Dosis")
    frequency = models.CharField(max_length=100, verbose_name="Frecuencia")
    duration = models.CharField(max_length=50, verbose_name="Duración del Tratamiento")
    instructions = models.TextField(blank=True, verbose_name="Instrucciones Especiales")
     
    def __str__(self):
        return f"Receta de {self.medication} para {self.medical_record.patient}"
    
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