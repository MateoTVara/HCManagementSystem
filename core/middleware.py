from django.shortcuts import redirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class AuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("Middleware triggered for:", request.path)
        exempt_paths = [
            settings.LOGIN_URL,
            '/logout/',
            '/admin/',
            '/static/',
            '/media/'
        ]
        
        # Verifica si la URL está en la lista de excepciones
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
        
        if not request.user.is_authenticated:
            print("Redirecting to login...")
            return redirect(settings.LOGIN_URL)