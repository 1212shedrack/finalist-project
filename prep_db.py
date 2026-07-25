import os
import django

def prep_db():
    """
    Ensures PostgreSQL schema 'amaranthus' exists before running migrations,
    providing complete table & migration isolation from other projects sharing cadts-db.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amaranthus_project.settings')
    django.setup()
    
    from django.db import connection
    
    try:
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute("CREATE SCHEMA IF NOT EXISTS amaranthus;")
                print("[SUCCESS] PostgreSQL schema 'amaranthus' created/verified.")
    except Exception as e:
        print(f"[NOTE] Database prep note: {e}")

if __name__ == '__main__':
    prep_db()
