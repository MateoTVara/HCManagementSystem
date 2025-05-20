from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Doctor, Patient, Appointment,
    Department, MedicalRecord, Medication,
    Prescription, Allergy, EmergencyContact,
    Room, Bed, Admission
)

# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'license_number')
    list_filter = ('department',)
    search_fields = ('user__first_name', 'user__last_name', 'license_number')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'gender', 'blood_type')
    list_filter = ('gender', 'blood_type')
    search_fields = ('first_name', 'last_name')
    ordering = ('last_name', 'first_name')
    
    def full_name(self, obj):
        return f"{obj.last_name}, {obj.first_name}"
    full_name.short_description = 'Nombre completo'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'doctor__department')
    date_hierarchy = 'date'
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__user__last_name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name',)
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Descripción'

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'diagnosis_short', 'attending_doctor', 'created_at')
    list_filter = ('attending_doctor__department', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'diagnosis')
    
    def diagnosis_short(self, obj):
        return obj.diagnosis[:50] + '...' if len(obj.diagnosis) > 50 else obj.diagnosis
    diagnosis_short.short_description = 'Diagnóstico'

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'dosage_form', 'strength', 'quantity_in_stock', 'expiration_status')
    list_filter = ('dosage_form', 'manufacturer')
    search_fields = ('name', 'generic_name')
    readonly_fields = ('quantity_in_stock',)
    
    def expiration_status(self, obj):
        from django.utils import timezone
        if obj.expiration_date < timezone.now().date():
            return "Expirado"
        elif (obj.expiration_date - timezone.now().date()).days < 30:
            return "Próximo a expirar"
        return "Válido"
    expiration_status.short_description = 'Estado'

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medical_record', 'medication', 'status', 'duration')
    list_filter = ('status', 'medication__dosage_form')
    raw_id_fields = ('medical_record',)

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('patient', 'name', 'severity', 'first_diagnosed')
    list_filter = ('severity',)
    search_fields = ('patient__first_name', 'patient__last_name', 'name')

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('patient', 'full_name', 'relationship', 'phone')
    search_fields = ('patient__first_name', 'patient__last_name', 'full_name')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'type', 'department')
    list_filter = ('type', 'department')
    search_fields = ('number',)

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'room', 'status')
    list_filter = ('status', 'room__type')
    search_fields = ('bed_number', 'room__number')

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'bed', 'admission_date', 'discharge_status')
    list_filter = ('bed__room__type',)
    date_hierarchy = 'admission_date'
    
    def discharge_status(self, obj):
        return "Alta dada" if obj.discharge_date else "Hospitalizado"
    discharge_status.short_description = 'Estado'

# Registro del modelo User personalizado
admin.site.register(User, CustomUserAdmin)