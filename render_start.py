#!/usr/bin/env python
import os
import sys
import subprocess
import django
from django.contrib.auth.models import User

def setup_admin_user():
    """Create the default admin user if it doesn't exist."""
    try:
        # Setup Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
        django.setup()
        
        # Check if BEKFURR user exists
        if not User.objects.filter(username='BEKFURR').exists():
            print("Creating default admin user 'BEKFURR'...")
            user = User.objects.create_user(
                username='BEKFURR',
                email='bekfurr@example.com',
                password='BEKFURR'
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print("Default admin user created successfully!")
        else:
            print("Default admin user already exists.")
    except Exception as e:
        print(f"Error setting up admin user: {e}")

def main():
    """
    Special startup script for Render.com deployment.
    This script ensures the application binds to the correct port
    and creates the default admin user.
    """
    # Get port from environment variable (for Render.com)
    port = os.environ.get('PORT', '8000')
    
    print(f"Starting application on port {port}...")
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
    
    # Setup admin user
    setup_admin_user()
    
    try:
        # Try to use Daphne (for WebSocket support)
        print(f"Attempting to start Daphne on port {port}...")
        subprocess.run([
            'daphne',
            '--bind', '0.0.0.0',
            '--port', port,
            'sign_language_project.asgi:application'
        ], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Daphne failed: {e}")
        print("Falling back to Django development server...")
        
        # Import Django's execute_from_command_line
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        
        # Run Django development server with explicit port binding
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])

if __name__ == '__main__':
    main()
