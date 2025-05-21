#!/usr/bin/env python
import os
import sys
import subprocess
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the Django server with Daphne for WebSocket support."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
    
    # Get port from environment variable (for Render.com and other cloud platforms)
    port = os.environ.get('PORT', '8000')
    
    # Run database initialization first
    logger.info("Initializing database...")
    try:
        from init_db import main as init_db_main
        init_result = init_db_main()
        if init_result != 0:
            logger.warning("Database initialization returned non-zero code. Continuing anyway...")
    except Exception as e:
        logger.error(f"Error running database initialization: {e}")
    
    # Check if Daphne is installed and available in PATH
    daphne_path = shutil.which('daphne')
    
    if daphne_path:
        logger.info(f"Found Daphne at: {daphne_path}")
        try:
            # Try to use Daphne (for WebSocket support)
            logger.info(f"Starting server with Daphne for WebSocket support on port {port}...")
            
            # Use subprocess.call to start Daphne and wait for it to complete
            return_code = subprocess.call([
                daphne_path,
                '-b', '0.0.0.0',
                '-p', port,
                'sign_language_project.asgi:application'
            ])
            
            if return_code != 0:
                logger.error(f"Daphne exited with code: {return_code}")
                logger.info("Falling back to Django development server...")
                fallback_to_django(port)
                
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
