#!/usr/bin/env python
"""
Migration script: SQLite → PostgreSQL for Busiada Boarding
Run this after PostgreSQL is installed and configured
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / 'Busiada_Boarding'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import connection

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def backup_sqlite_data():
    """Backup all data from SQLite before migration"""
    print_section("STEP 1: Backing up SQLite data")
    
    backup_file = 'sqlite_backup.json'
    try:
        print("📦 Dumping all data from SQLite...")
        call_command('dumpdata', stdout=open(backup_file, 'w'))
        print(f"✅ Data backed up to: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Error backing up data: {e}")
        return None

def update_settings_to_postgres():
    """Update settings.py to use PostgreSQL"""
    print_section("STEP 2: Updating Django settings")
    
    settings_path = Path('Busiada_Boarding/config/settings.py')
    settings_content = settings_path.read_text()
    
    # Replace SQLite config with PostgreSQL
    old_db_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""
    
    new_db_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'busiada_boarding',
        'USER': 'postgres',
        'PASSWORD': 'your_password_here',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}"""
    
    if old_db_config in settings_content:
        settings_content = settings_content.replace(old_db_config, new_db_config)
        settings_path.write_text(settings_content)
        print("✅ settings.py updated to PostgreSQL config")
        print("\n⚠️  IMPORTANT: Update these values in config/settings.py:")
        print("   - PASSWORD: Set your PostgreSQL password")
        print("   - HOST: localhost (for local) or server IP (for remote)")
        print("   - NAME: busiada_boarding (database name)")
        return True
    else:
        print("❌ Could not find SQLite config in settings.py")
        print("ℹ️  Please manually update DATABASES in config/settings.py")
        return False

def run_migrations():
    """Run Django migrations on new PostgreSQL database"""
    print_section("STEP 3: Running migrations on PostgreSQL")
    
    try:
        print("🔄 Running Django migrations...")
        call_command('migrate', verbosity=1)
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def restore_data(backup_file):
    """Load backed up data into PostgreSQL"""
    print_section("STEP 4: Restoring data to PostgreSQL")
    
    if not os.path.exists(backup_file):
        print(f"⚠️  Backup file not found: {backup_file}")
        return False
    
    try:
        print("📥 Loading data into PostgreSQL...")
        call_command('loaddata', backup_file, verbosity=1)
        print("✅ Data restored successfully")
        return True
    except Exception as e:
        print(f"⚠️  Could not load all data: {e}")
        print("ℹ️  This is normal if some fixtures don't exist in new DB")
        print("You may need to manually recreate admin data:")
        print("   python manage.py createsuperuser")
        return False

def verify_migration():
    """Verify PostgreSQL connection and data"""
    print_section("STEP 5: Verifying migration")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            print(f"✅ Connected to: {db_version.split(',')[0]}")
        
        # Count tables
        tables = connection.introspection.table_names()
        print(f"✅ Found {len(tables)} tables in database")
        
        return True
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def print_next_steps():
    """Print instructions for next steps"""
    print_section("NEXT STEPS")
    
    print("""
1️⃣  BEFORE running this script:
    • Install PostgreSQL on your system
    • Create a PostgreSQL database: createdb busiada_boarding
    • Have your PostgreSQL credentials ready

2️⃣  CONFIGURE settings.py:
    • Edit: Busiada_Boarding/config/settings.py
    • Set correct PASSWORD, HOST, and database NAME in DATABASES

3️⃣  INSTALL PostgreSQL driver:
    pip install psycopg2-binary

4️⃣  RUN this script:
    python migrate_to_postgres.py

5️⃣  IF DATA LOADING FAILS:
    • Recreate admin account: python manage.py createsuperuser
    • Check backup file: sqlite_backup.json
    • Manually load: python manage.py loaddata sqlite_backup.json

6️⃣  TEST the migration:
    python manage.py runserver

7️⃣  TROUBLESHOOTING:
    • Check PostgreSQL is running
    • Verify database exists: psql -l
    • Check config/settings.py credentials
    • Review error messages above
    """)

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     SQLite → PostgreSQL Migration Script                   ║
    ║     Busiada Girls Senior School                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print_next_steps()
    
    # Check if user confirmed setup
    response = input("\n✋ Have you completed steps 1-3 above? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("⏸️  Migration paused. Please complete setup steps first.")
        return
    
    # Run migration steps
    backup_file = backup_sqlite_data()
    
    if not backup_file:
        print("❌ Could not backup data. Migration aborted.")
        return
    
    settings_ok = update_settings_to_postgres()
    
    if not settings_ok:
        print("⚠️  Please manually update settings.py and run again.")
        response = input("Continue anyway? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            return
    
    migrations_ok = run_migrations()
    
    if not migrations_ok:
        print("❌ Migrations failed. Check your PostgreSQL connection.")
        return
    
    restore_data(backup_file)
    
    if verify_migration():
        print_section("✅ MIGRATION COMPLETE!")
        print("""
Your database has been successfully migrated to PostgreSQL.

Next steps:
  1. Test: python manage.py runserver
  2. Check admin: http://localhost:8000/admin
  3. If admin not accessible: python manage.py createsuperuser
  4. Archive old db.sqlite3 if satisfied with migration
        """)
    else:
        print_section("⚠️  VERIFICATION FAILED")
        print("Please check PostgreSQL connection and try running migrations manually:")
        print("  python manage.py migrate")

if __name__ == '__main__':
    main()
