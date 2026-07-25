import os
import django

def prep_db():
    """
    Checks if the shared database has leftover django_migrations records
    from a previous project while missing the actual tables (like auth_user).
    If so, clears django_migrations so Django can run all migrations cleanly.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amaranthus_project.settings')
    django.setup()
    
    from django.db import connection
    
    try:
        engine = connection.vendor
        if engine != 'postgresql':
            print(f"[INFO] Database engine is '{engine}', skipping stale history check.")
            return
            
        with connection.cursor() as cursor:
            # Check if auth_user table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'auth_user'
                );
            """)
            row = cursor.fetchone()
            auth_user_exists = row[0] if row else False
            
            # Check if django_migrations table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'django_migrations'
                );
            """)
            row = cursor.fetchone()
            migrations_exists = row[0] if row else False
            
            # If django_migrations exists BUT auth_user does NOT, clear stale history
            if migrations_exists and not auth_user_exists:
                print("[INFO] Cleaning stale migration history from shared database...")
                cursor.execute("DROP TABLE IF EXISTS django_migrations CASCADE;")
                print("[SUCCESS] Cleared stale migration history.")
            else:
                print("[INFO] Database schema state verified.")
    except Exception as e:
        print(f"[NOTE] Database prep check skipped: {e}")

if __name__ == '__main__':
    prep_db()
