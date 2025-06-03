from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Doctor, Patient, Appointment,
    MedicalRecord, Medication,
    Prescription, EmergencyContact,
    Admission, Allergy, PatientAllergy,
    MedicalExam
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'dni', 'gender')
    list_filter = ('specialty', 'gender')
    search_fields = ('user__first_name', 'user__last_name', 'dni')

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('name', 'common_reactions')
    search_fields = ('name',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'dni', 'date_of_birth', 'gender', 'blood_type', 'phone', 'email')
    list_filter = ('gender', 'blood_type')
    search_fields = ('first_name', 'last_name', 'dni')
    ordering = ('last_name', 'first_name')
    
    def full_name(self, obj):
        return f"{obj.last_name}, {obj.first_name}"
    full_name.short_description = 'Nombre completo'

@admin.register(PatientAllergy)
class PatientAllergyAdmin(admin.ModelAdmin):
    list_display = ('patient', 'allergy', 'severity', 'patient_reactions', 'date_registered')
    list_filter = ('severity',)
    search_fields = ('patient__first_name', 'patient__last_name', 'allergy__name')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status', 'diagnosis_short', 'reason_short')
    list_filter = ('status', 'doctor__specialty')
    date_hierarchy = 'date'
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__user__last_name', 'diagnosis', 'reason')

    def diagnosis_short(self, obj):
        return obj.diagnosis[:30] + '...' if obj.diagnosis and len(obj.diagnosis) > 30 else obj.diagnosis
    diagnosis_short.short_description = 'Diagnóstico'

    def reason_short(self, obj):
        return obj.reason[:30] + '...' if obj.reason and len(obj.reason) > 30 else obj.reason
    reason_short.short_description = 'Motivo'

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'attending_doctor', 'created_at', 'status')
    list_filter = ('attending_doctor__specialty', 'created_at', 'status')
    search_fields = ('patient__first_name', 'patient__last_name')

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'dosage_form', 'strength', 'quantity_in_stock', 'manufacturer')
    list_filter = ('dosage_form', 'manufacturer')
    search_fields = ('name', 'generic_name')
    readonly_fields = ('quantity_in_stock',)

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'medication', 'dosage', 'frequency', 'duration')
    list_filter = ('medication__dosage_form',)
    raw_id_fields = ('appointment',)

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('patient', 'full_name', 'relationship', 'phone')
    search_fields = ('patient__first_name', 'patient__last_name', 'full_name')

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'admission_date', 'discharge_status')
    date_hierarchy = 'admission_date'
    
    def discharge_status(self, obj):
        return "Alta dada" if obj.discharge_date else "Hospitalizado"
    discharge_status.short_description = 'Estado'

@admin.register(MedicalExam)
class MedicalExamAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'exam_type')
    list_filter = ('exam_type',)
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name')