#!/usr/bin/env python
import os
import sys
import subprocess
import time
import logging
import shutil

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
    
    # Check if Daphne is installed and available in PATH
    daphne_path = shutil.which('daphne')
    
    if daphne_path:
        logger.info(f"Found Daphne at: {daphne_path}")
        try:
            # Try to use Daphne (for WebSocket support)
            logger.info(f"Attempting to start Daphne on port {port}...")
            
            # Use subprocess.Popen to start Daphne
            daphne_process = subprocess.Popen([
                daphne_path,
                '-b', '0.0.0.0',
                '-p', port,
                'sign_language_project.asgi:application'
            ])
            
            # Log the process ID
            logger.info(f"Daphne started with PID: {daphne_process.pid}")
            
            # Wait for the process to complete
            daphne_process.wait()
            
            # If we get here, Daphne has exited
            logger.error(f"Daphne exited with code: {daphne_process.returncode}")
            
        except Exception as e:
            logger.error(f"Error starting Daphne: {e}")
            logger.info("Falling back to Django development server...")
            fallback_to_django(port)
    else:
        logger.warning("Daphne not found in PATH. Falling back to Django development server...")
        fallback_to_django(port)

def fallback_to_django(port):
    """Fall back to Django development server if Daphne fails."""
    try:
        # Import Django's execute_from_command_line
        from django.core.management import execute_from_command_line
        
        # Run Django development server with explicit port binding
        logger.info(f"Starting Django development server on port {port}...")
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])
    except ImportError as exc:
        logger.error(f"Error importing Django: {exc}")
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    except Exception as e:
        logger.error(f"Error starting Django development server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
