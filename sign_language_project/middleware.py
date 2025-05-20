from django.contrib.auth.models import User
from django.contrib.auth import login

class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Auto-login if not authenticated
        if not request.user.is_authenticated:
            try:
                # Get or create default user
                user, created = User.objects.get_or_create(
                    username='BEKFURR',
                    defaults={
                        'email': 'bekfurr@example.com',
                        'is_staff': True,
                        'is_superuser': True,
                    }
                )
                if created:
                    user.set_password('BEKFURR')
                    user.save()
                
                # Login the user
                login(request, user)
            except Exception as e:
                print(f"Auto-login error: {e}")
        
        response = self.get_response(request)
        return response
