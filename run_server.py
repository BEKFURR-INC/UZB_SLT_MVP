#!/usr/bin/env python
import os
import sys
import subprocess
import logging
import django

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with migrations."""
    try:
        # Setup Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
        django.setup()
        
        from django.db import connection
        
        # Check existing tables
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.info(f"Existing tables: {[t[0] for t in tables]}")
        
        # Apply migrations
        from django.core.management import execute_from_command_line
        
        logger.info("Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', 'translator'])
        
        logger.info("Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Verify tables after migration
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.info(f"Tables after migration: {[t[0] for t in tables]}")
        
        # Check if required tables exist
        required_tables = ['translator_trainedmodel', 'translator_translationsession', 'translator_signvideo']
        missing_tables = [table for table in required_tables if table not in [t[0] for t in tables]]
        
        if missing_tables:
            logger.error(f"Missing required tables: {missing_tables}")
            return False
        else:
            logger.info("All required tables exist!")
            
        # Create default admin user
        from django.contrib.auth.models import User
        if not User.objects.filter(username='BEKFURR').exists():
            user = User.objects.create_superuser('BEKFURR', 'bekfurr@example.com', 'BEKFURR')
            logger.info("Created default admin user: BEKFURR")
        else:
            logger.info("Default admin user already exists.")
            
        logger.info("Database initialization completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
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
    """Run the Django server with Daphne for WebSocket support."""
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Create static directory
    create_static_directory()
    
    # Get port from environment variable (for Render.com and other cloud platforms)
    port = os.environ.get('PORT', '8000')
    
    try:
        # Check if Daphne is installed
        daphne_path = subprocess.check_output(['which', 'daphne']).decode().strip()
        logger.info(f"Found Daphne at: {daphne_path}")
        
        # Initialize Django before starting Daphne
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
        django.setup()
        
        logger.info(f"Starting server with Daphne for WebSocket support on port {port}...")
        
        # Run Daphne server with the PORT environment variable
        subprocess.run([
            daphne_path,
            '--bind', '0.0.0.0',
            '--port', port,
            'sign_language_project.asgi:application'
        ])
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Daphne not found. Please install it with: pip install daphne")
        logger.info("Falling back to standard Django development server (WebSockets won't work)...")
        
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
        logger.info(f"Starting Django development server on port {port}...")
        execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}'])

if __name__ == '__main__':
    main()
