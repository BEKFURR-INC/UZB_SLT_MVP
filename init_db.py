#!/usr/bin/env python
import os
import sys
import django
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Initialize the database by creating all necessary tables.
    This script should be run before starting the application.
    """
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
    
    try:
        # Initialize Django
        django.setup()
        
        # Import Django models and management commands
        from django.db import connection
        from django.core.management import call_command
        
        # Check if tables exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.info(f"Existing tables: {[t[0] for t in tables]}")
        
        # Create migrations if they don't exist
        logger.info("Creating migrations...")
        call_command('makemigrations', 'translator', interactive=False)
        
        # Apply migrations
        logger.info("Applying migrations...")
        call_command('migrate', interactive=False)
        
        # Verify tables were created
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            logger.info(f"Tables after migration: {[t[0] for t in tables]}")
            
            # Check for specific tables
            required_tables = [
                'translator_trainedmodel',
                'translator_signvideo',
                'translator_translationsession'
            ]
            
            missing_tables = [table for table in required_tables if f"{table}" not in [t[0] for t in tables]]
            
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                logger.info("Attempting to create tables directly...")
                
                # Create tables directly if migrations failed
                from translator.models import TrainedModel, SignVideo, TranslationSession
                
                # Force creation of tables
                with connection.schema_editor() as schema_editor:
                    for model in [TrainedModel, SignVideo, TranslationSession]:
                        if model._meta.db_table in missing_tables:
                            logger.info(f"Creating table for {model._meta.db_table}")
                            schema_editor.create_model(model)
                
                # Verify again
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    logger.info(f"Tables after direct creation: {[t[0] for t in tables]}")
            else:
                logger.info("All required tables exist!")
        
        # Create default superuser
        from django.contrib.auth.models import User
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
        
        logger.info("Database initialization completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == '__main__':
    sys.exit(main())
