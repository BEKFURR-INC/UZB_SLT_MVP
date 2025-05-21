import logging
import traceback
from django.db import connection
from django.core.management import call_command

logger = logging.getLogger(__name__)

class DatabaseInitMiddleware:
    """
    Middleware to ensure database tables exist before processing requests.
    This will check for required tables and create them if they don't exist.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.initialized = False
        self.required_tables = [
            'translator_trainedmodel',
            'translator_signvideo',
            'translator_translationsession'
        ]
    
    def __call__(self, request):
        # Only run initialization once per server startup
        if not self.initialized:
            self.initialize_database()
            self.initialized = True
        
        # Process the request
        response = self.get_response(request)
        return response
    
    def initialize_database(self):
        """Initialize the database by creating required tables if they don't exist."""
        try:
            logger.info("Checking database tables...")
            missing_tables = self.get_missing_tables()
            
            if missing_tables:
                logger.warning(f"Missing tables detected: {missing_tables}")
                self.create_tables()
                
                # Verify tables were created
                missing_tables = self.get_missing_tables()
                if missing_tables:
                    logger.error(f"Failed to create tables: {missing_tables}")
                else:
                    logger.info("All required tables created successfully!")
            else:
                logger.info("All required tables exist!")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            logger.error(traceback.format_exc())
    
    def get_missing_tables(self):
        """Get a list of required tables that don't exist in the database."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                existing_tables = [row[0] for row in cursor.fetchall()]
                
            return [table for table in self.required_tables if table not in existing_tables]
        except Exception as e:
            logger.error(f"Error checking tables: {e}")
            return self.required_tables  # Assume all tables are missing if there's an error
    
    def create_tables(self):
        """Create database tables by applying migrations."""
        try:
            logger.info("Creating migrations...")
            call_command('makemigrations', 'translator', interactive=False)
            
            logger.info("Applying migrations...")
            call_command('migrate', interactive=False)
            
            # If migrations fail, try creating tables directly
            missing_tables = self.get_missing_tables()
            if missing_tables:
                logger.warning(f"Migrations didn't create all tables. Trying direct creation for: {missing_tables}")
                self.create_tables_directly(missing_tables)
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            logger.error(traceback.format_exc())
    
    def create_tables_directly(self, missing_tables):
        """Create tables directly using Django's schema editor."""
        try:
            from django.apps import apps
            from django.db import connection
            
            # Get the models for the missing tables
            app_label = 'translator'
            models = []
            
            for table_name in missing_tables:
                model_name = table_name.replace(f"{app_label}_", "")
                try:
                    model = apps.get_model(app_label, model_name)
                    models.append(model)
                except LookupError:
                    logger.error(f"Could not find model for table {table_name}")
            
            # Create tables directly
            with connection.schema_editor() as schema_editor:
                for model in models:
                    logger.info(f"Creating table for {model._meta.db_table}")
                    schema_editor.create_model(model)
        except Exception as e:
            logger.error(f"Error creating tables directly: {e}")
            logger.error(traceback.format_exc())
