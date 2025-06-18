from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required, login_required
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

@login_not_required
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_url if next_url else 'dashboard')
        return render(request, 'login.html', {
            'error': 'Credenciales inválidas',
            'next': next_url
        })
    return render(request, 'login.html', {'next': next_url})

def logout_view(request):
    logout(request)
    return redirect('login')

class DashboardView(View):
    def get(self, request):
        return render(request, 'dashboard.html')

@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        errors = []

        # Validaciones básicas
        if not first_name:
            errors.append("El nombre es obligatorio.")
        if not last_name:
            errors.append("El apellido es obligatorio.")
        if not email:
            errors.append("El correo electrónico es obligatorio.")
        if not username:
            errors.append("El usuario es obligatorio.")

        # Validar usuario único si lo cambia
        if username != user.username:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                errors.append("El nombre de usuario ya está en uso.")

        # Validar contraseña solo si se intenta cambiar
        if password1 or password2:
            if password1 != password2:
                errors.append("Las contraseñas no coinciden.")
            elif len(password1) < 6:
                errors.append("La contraseña debe tener al menos 6 caracteres.")

        if errors:
            return render(request, 'user_profile.html', {'user': user, 'errors': errors})

        # Guardar cambios
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        if password1:
            user.set_password(password1)
        user.save()
        if password1:
            update_session_auth_hash(request, user)  # Mantiene la sesión activa tras cambiar contraseña
        return render(request, 'user_profile.html', {'user': user, 'success': True})
    return render(request, 'user_profile.html', {'user': user})