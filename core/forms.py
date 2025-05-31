from django import forms
from .models import Appointment, Patient, PatientAllergy, Allergy, Doctor, User

class AppointmentRegister(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'patient': forms.Select(attrs={
                'class': 'form-select'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }

class AppointmentEdit(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time', 'reason', 'status'
                  ]
        widgets = {
            'date' : forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'time' : forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'patient' : forms.Select(attrs={
                'class': 'form-select'
            }),
            'doctor' : forms.Select(attrs={
                'class': 'form-select'
            }),
            'reason' : forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'status' : forms.Select(attrs={
                'class': 'form-select'
            }),
        }

class AllergyRegister(forms.ModelForm):
    class Meta:
        model = Allergy
        fields = ['name', 'common_reactions']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'common_reactions': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }

class PatientRegister(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['dni', 'first_name', 'last_name', 'date_of_birth', 'gender', 'blood_type',
                  'phone', 'address', 'email', 'allergies']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'blood_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'address': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'allergies': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allergies = Allergy.objects.all()
        for allergy in self.allergies:
            self.fields[f'allergy_{allergy.id}'] = forms.BooleanField(
                required=False,
                label=allergy.name
            )
            self.fields[f'severity_{allergy.id}'] = forms.ChoiceField(
                choices=PatientAllergy.SEVERITY_CHOICES,
                required=False,
                label="Severidad"
            )
            self.fields[f'reactions_{allergy.id}'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
                required=False,
                label="Reacciones"
            )
    
    def save(self, commit=True):
        patient = super().save(commit)
        for allergy in Allergy.objects.all():
            if self.cleaned_data.get(f'allergy_{allergy.id}'):
                PatientAllergy.objects.update_or_create(
                    patient=patient,
                    allergy=allergy,
                    defaults={
                        'severity': self.cleaned_data[f'severity_{allergy.id}'],
                        'patient_reactions': self.cleaned_data[f'reactions_{allergy.id}']
                    }
                )
        return patient
    
class PatientEdit(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['dni', 'first_name', 'last_name', 'date_of_birth', 'gender'
                  , 'blood_type', 'phone', 'address', 'email', 'allergies']
        widgets = {
            'dni' : forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'blood_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'allergies': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allergies = Allergy.objects.all()
        for allergy in self.allergies:
            self.fields[f'allergy_{allergy.id}'] = forms.BooleanField(
                required=False,
                label=allergy.name,
                initial=self.instance.allergies.filter(id=allergy.id).exists() if self.instance.pk else False
            )
            self.fields[f'severity_{allergy.id}'] = forms.ChoiceField(
                choices=PatientAllergy.SEVERITY_CHOICES,
                required=False,
                label="Severidad",
                initial=PatientAllergy.objects.filter(patient=self.instance, allergy=allergy).first().severity if self.instance.pk and PatientAllergy.objects.filter(patient=self.instance, allergy=allergy).exists() else ''
            )
            self.fields[f'reactions_{allergy.id}'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
                required=False,
                label="Reacciones",
                initial=PatientAllergy.objects.filter(patient=self.instance, allergy=allergy).first().patient_reactions if self.instance.pk and PatientAllergy.objects.filter(patient=self.instance, allergy=allergy).exists() else ''
            )

    def save(self, commit=True):
        patient = super().save(commit)
        selected_allergy_ids = []
        for allergy in Allergy.objects.all():
            if self.cleaned_data.get(f'allergy_{allergy.id}'):
                selected_allergy_ids.append(allergy.id)
                PatientAllergy.objects.update_or_create(
                    patient=patient,
                    allergy=allergy,
                    defaults={
                        'severity': self.cleaned_data.get(f'severity_{allergy.id}', ''),
                        'patient_reactions': self.cleaned_data.get(f'reactions_{allergy.id}', '')
                    }
                )
        PatientAllergy.objects.filter(patient=patient).exclude(allergy_id__in=selected_allergy_ids).delete()
        return patient

class DoctorUserEdit(forms.ModelForm):
    # Campos del usuario
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)
    email = forms.EmailField(label="Correo electrónico")

    class Meta:
        model = Doctor
        fields = ['specialty', 'dni', 'first_name', 'last_name', 'email']
        widgets = {
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.setdefault('initial', {})
        if instance:
            initial['first_name'] = instance.user.first_name
            initial['last_name'] = instance.user.last_name
            initial['email'] = instance.user.email
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        doctor = super().save(commit=False)
        user = doctor.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            doctor.save()
        return doctor