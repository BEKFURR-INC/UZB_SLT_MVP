#!/usr/bin/env python
import os
import sys
import subprocess
import django
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Apply migrations and create initial database structure."""
    try:
        logger.info("Applying database migrations...")
        from django.core.management import execute_from_command_line
        
        # Make migrations first to ensure they exist
        logger.info("Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', 'translator'])
        
        # Then apply migrations
        logger.info("Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Verify tables exist
        logger.info("Verifying database tables...")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.info(f"Database tables: {[t[0] for t in tables]}")
        
        logger.info("Database migrations applied successfully!")
        return True
    except Exception as e:
        logger.error(f"Error applying migrations: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def setup_admin_user():
    """Create the default admin user if it doesn't exist."""
    try:
        # Setup Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
        django.setup()
        
        from django.contrib.auth.models import User
        
        # Check if BEKFURR user exists
        if not User.objects.filter(username='BEKFURR').exists():
            logger.info("Creating default admin user 'BEKFURR'...")
            user = User.objects.create_user(
                username='BEKFURR',
                email='bekfurr@example.com',
                password='BEKFURR'
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            logger.info("Default admin user created successfully!")
        else:
            logger.info("Default admin user already exists.")
        return True
    except Exception as e:
        logger.error(f"Error setting up admin user: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def create_static_directory():
    """Create the static directory if it doesn't exist."""
    try:
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        if not os.path.exists(static_dir):
            logger.info(f"Creating static directory at {static_dir}")
            os.makedirs(static_dir, exist_ok=True)
            logger.info("Static directory created successfully!")
        else:
            logger.info("Static directory already exists.")
        return True
    except Exception as e:
        logger.error(f"Error creating static directory: {e}")
        return False

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
    
    # Initialize database
    logger.info("Initializing database...")
    
    # Create static directory
    create_static_directory()
    
    # Setup database first - retry up to 3 times
    success = False
    for attempt in range(3):
        logger.info(f"Database setup attempt {attempt + 1}/3")
        if setup_database():
            success = True
            break
        else:
            logger.warning(f"Database setup failed, retrying in 5 seconds...")
            time.sleep(5)
    
    if not success:
        logger.error("Failed to set up database after 3 attempts. Starting server anyway...")
    
    # Then setup admin user
    setup_admin_user()
    
    try:
        # Check if Daphne is installed and available
        daphne_path = None
        try:
            daphne_path = subprocess.check_output(['which', 'daphne']).decode().strip()
            logger.info(f"Found Daphne at: {daphne_path}")
        except subprocess.CalledProcessError:
            logger.warning("Daphne not found in PATH")
        
        if daphne_path:
            # Try to use Daphne (for WebSocket support)
            logger.info(f"Starting server with Daphne for WebSocket support on port {port}...")
            
            # Initialize Django before starting Daphne
            django.setup()
            
            # Start Daphne with the correct module
            subprocess.run([
                daphne_path,
                '--bind', '0.0.0.0',
                '--port', port,
                'sign_language_project.asgi:application'
            ], check=True)
        else:
            raise FileNotFoundError("Daphne not found")
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
        logger.info(f"Starting Django development server on port {port}...")
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])

if __name__ == '__main__':
    main()
