from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required
from django.views.generic import View

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