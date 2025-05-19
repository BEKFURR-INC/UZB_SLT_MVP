#!/usr/bin/env python
import os
import sys
import subprocess

def main():
    """Run the Django server with Daphne for WebSocket support."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
    
    # Get port from environment variable (for Render.com and other cloud platforms)
    port = os.environ.get('PORT', '8000')
    
    try:
        # Check if Daphne is installed
        subprocess.run(['daphne', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Starting server with Daphne for WebSocket support on port {port}...")
        
        # Run Daphne server with the PORT environment variable
        subprocess.run(['daphne', '-b', '0.0.0.0', '-p', port, 'sign_language_project.asgi:application'])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Daphne not found. Please install it with: pip install daphne")
        print("Falling back to standard Django development server (WebSockets won't work)...")
        
        # Import Django's execute_from_command_line
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        
        # Run Django development server with the PORT environment variable
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])

if __name__ == '__main__':
    main()
