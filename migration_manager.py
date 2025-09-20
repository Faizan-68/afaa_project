#!/usr/bin/env python3
"""
Migration Management Script for AFAA Project
============================================

This script helps manage Django migrations for production deployment.
Run this before deploying to ensure database consistency.

Usage:
    python migration_manager.py --check     # Check migration status
    python migration_manager.py --plan      # Show migration plan
    python migration_manager.py --apply     # Apply migrations
    python migration_manager.py --backup    # Create database backup
"""

import os
import sys
import subprocess
from datetime import datetime
import shutil

def run_command(cmd):
    """Execute a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_migrations():
    """Check current migration status"""
    print("🔍 Checking migration status...")
    
    success, output, error = run_command("python manage.py showmigrations")
    if success:
        print("✅ Migration Status:")
        print(output)
    else:
        print(f"❌ Error checking migrations: {error}")
        return False
    
    # Check for unapplied model changes
    success, output, error = run_command("python manage.py makemigrations --dry-run")
    if "No changes detected" in output:
        print("✅ All models are up to date with migrations")
    else:
        print("⚠️  Unapplied model changes detected:")
        print(output)
        return False
    
    return True

def create_backup():
    """Create database backup"""
    if os.path.exists('db.sqlite3'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'db_backup_{timestamp}.sqlite3'
        shutil.copy2('db.sqlite3', backup_name)
        print(f"✅ Database backup created: {backup_name}")
        return backup_name
    else:
        print("❌ Database file not found")
        return None

def show_migration_plan():
    """Show what migrations would be applied"""
    print("📋 Migration Plan:")
    
    success, output, error = run_command("python manage.py showmigrations --plan")
    if success:
        print(output)
    else:
        print(f"❌ Error getting migration plan: {error}")

def apply_migrations():
    """Apply all pending migrations"""
    print("🚀 Applying migrations...")
    
    # First, create backup
    backup = create_backup()
    if not backup:
        print("❌ Could not create backup. Aborting migration.")
        return False
    
    # Apply migrations
    success, output, error = run_command("python manage.py migrate")
    if success:
        print("✅ Migrations applied successfully:")
        print(output)
        return True
    else:
        print(f"❌ Error applying migrations: {error}")
        print(f"💾 Database backup available at: {backup}")
        return False

def validate_database():
    """Validate database integrity"""
    print("🔎 Validating database integrity...")
    
    success, output, error = run_command("python manage.py check --database default")
    if success:
        print("✅ Database validation passed")
        return True
    else:
        print(f"❌ Database validation failed: {error}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == "--check":
        check_migrations()
        validate_database()
    
    elif command == "--plan":
        show_migration_plan()
    
    elif command == "--apply":
        if check_migrations():
            print("ℹ️  All migrations are already applied")
        else:
            apply_migrations()
            validate_database()
    
    elif command == "--backup":
        create_backup()
    
    else:
        print("❌ Unknown command. Use --check, --plan, --apply, or --backup")

if __name__ == "__main__":
    main()