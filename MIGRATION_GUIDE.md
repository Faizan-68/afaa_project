# Migration Management Guide for AFAA Project

## Current Status ✅
- **All migrations are properly applied** 
- **Database schema is consistent with models**
- **No pending migrations detected**
- **16 migration files in accounts app**

## Migration Files Structure
```
accounts/migrations/
├── 0001_initial.py                    # Initial user, plan models
├── 0002-0003_*.py                     # Plan & UserPlan updates  
├── 0004_*.py                          # TeamReward, Commission, Referral
├── 0005-0006_*.py                     # Payment & Course models
├── 0007-0008_*.py                     # Site settings & course links
├── 0009-0016_*.py                     # Recent plan & settings updates
```

## For Production Deployment

### 1. Pre-Deployment Checklist
```bash
# Always backup database first
python migration_manager.py --backup

# Check migration status
python manage.py showmigrations

# Check for model changes
python manage.py makemigrations --dry-run

# Validate database integrity
python manage.py check --database default
```

### 2. Safe Migration Process
```bash
# Step 1: Create backup
cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# Step 2: Test migrations on copy
python manage.py migrate --run-syncdb

# Step 3: Apply to production (if tests pass)
python manage.py migrate
```

### 3. Common Migration Issues & Solutions

#### Issue: Migration Conflicts
**Solution:**
```bash
python manage.py migrate accounts zero  # Reset app migrations
python manage.py migrate accounts       # Re-apply all migrations
```

#### Issue: Fake Migrations (when adding to existing project)
**Solution:**
```bash
python manage.py migrate --fake-initial
```

#### Issue: Database Schema Mismatch
**Solution:**
```bash
python manage.py migrate --run-syncdb
```

## Best Practices Implemented

### ✅ What's Already Good:
1. **Proper migration sequence** - All migrations have dependencies
2. **Descriptive migration names** - Easy to understand changes
3. **No circular dependencies** - Clean migration graph
4. **Backup strategy** - Database backup before changes

### 🔧 Recommendations for Future:

#### 1. Add Migration Validation Script
```python
# In settings.py - for production
MIGRATION_MODULES = {
    'accounts': 'accounts.migrations',
}
```

#### 2. Environment-Specific Settings
```python
# For production migrations
if not DEBUG:
    MIGRATION_MODULES = {
        'accounts': 'accounts.migrations_prod',
    }
```

#### 3. Zero-Downtime Migration Strategy
- Use `python manage.py migrate --plan` before applying
- Implement gradual rollout for large schema changes
- Use database transactions for critical migrations

## Deployment Commands

### For New Environment Setup:
```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up database
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Collect static files
python manage.py collectstatic --noinput
```

### For Production Updates:
```bash
# 1. Backup database
python migration_manager.py --backup

# 2. Pull latest code
git pull origin main

# 3. Install new dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Update static files
python manage.py collectstatic --noinput

# 6. Restart server
```

## Migration Monitoring

### Check Migration History:
```bash
python manage.py showmigrations --verbosity=2
```

### Reverse Migration (if needed):
```bash
python manage.py migrate accounts 0015  # Go back to specific migration
```

### Generate Migration SQL (for review):
```bash
python manage.py sqlmigrate accounts 0016
```

## Conclusion
Your migration system is **properly set up and healthy**! The main improvements made:

1. ✅ **Verified all migrations are applied**
2. ✅ **Confirmed database consistency** 
3. ✅ **Created backup strategy**
4. ✅ **Added migration management script**
5. ✅ **Documented best practices**

**Result**: Your project is now **production-ready** from a migration perspective! 🚀