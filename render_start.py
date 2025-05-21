#!/usr/bin/env python
import os
import sys
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Special startup script for Render.com deployment.
    This script ensures the application binds to the correct port
    and creates the default admin user.
    """
    # Get port from environment variable (for Render.com)
    port = os.environ.get('PORT', '8000')
    
    logger.info(f"Starting application on port {port}...")
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
    
    # Run database initialization script first
    logger.info("Initializing database...")
    db_init_result = subprocess.run([sys.executable, 'init_db.py'], check=False)
    
    if db_init_result.returncode != 0:
        logger.error("Database initialization failed! Application may not work correctly.")
    else:
        logger.info("Database initialization completed successfully!")
    
    # Wait a moment to ensure database is ready
    time.sleep(2)
    
    try:
        # Try to use Daphne (for WebSocket support)
        logger.info(f"Attempting to start Daphne on port {port}...")
        subprocess.run([
            'daphne',
            '--bind', '0.0.0.0',
            '--port', port,
            'sign_language_project.asgi:application'
        ], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Daphne failed: {e}")
        logger.info("Falling back to Django development server...")
        
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
