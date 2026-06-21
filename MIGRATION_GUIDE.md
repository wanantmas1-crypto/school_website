# SQLite → PostgreSQL Migration Guide
## Busiada Girls Senior School

**Duration:** ~10 minutes  
**Difficulty:** Easy  
**Risk:** Low (full backup created)

---

## ✅ Prerequisites

### 1. Install PostgreSQL
- **Windows:** Download from https://www.postgresql.org/download/windows/
- During installation:
  - Remember your **postgres** password
  - Keep default port: **5432**
  - Install pgAdmin (optional, helpful for management)

### 2. Verify Installation
Open PowerShell and run:
```powershell
psql --version
```
Should show: `psql (PostgreSQL) 15.x` (or higher)

### 3. Create Database
Open PowerShell as Administrator:
```powershell
psql -U postgres
```
Enter your postgres password, then:
```sql
CREATE DATABASE busiada_boarding;
\q
```

---

## 🚀 Migration Process

### Step 1: Prepare Python Dependencies
```powershell
cd c:\Users\user\Busiada_Boarding
.\venv\Scripts\activate

pip install psycopg2-binary
```

### Step 2: Update Django Settings
Edit `Busiada_Boarding/config/settings.py`

**Find this section:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Replace with:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'busiada_boarding',
        'USER': 'postgres',
        'PASSWORD': 'YOUR_POSTGRES_PASSWORD_HERE',  # Change this!
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

⚠️ **Important:** Replace `YOUR_POSTGRES_PASSWORD_HERE` with your actual postgres password

### Step 3: Run Migration Script
```powershell
cd c:\Users\user\Busiada_Boarding
python migrate_to_postgres.py
```

The script will:
1. ✅ Backup all SQLite data
2. ✅ Update settings.py
3. ✅ Run Django migrations
4. ✅ Restore data to PostgreSQL
5. ✅ Verify connection

### Step 4: Test Migration
```powershell
cd Busiada_Boarding
..\venv\Scripts\python.exe manage.py runserver
```

Visit: http://localhost:8000/admin

---

## 🔧 Troubleshooting

### ❌ "psql: command not found"
**Solution:** PostgreSQL not in PATH
- Reinstall PostgreSQL and check "Add to PATH" during install
- Or manually add: `C:\Program Files\PostgreSQL\15\bin` to System PATH

### ❌ "password authentication failed"
**Solution:** Wrong postgres password in settings.py
```powershell
# Reset postgres password
psql -U postgres -c "ALTER USER postgres PASSWORD 'newpassword';"
# Update settings.py with new password
```

### ❌ "database busiada_boarding does not exist"
**Solution:** Database not created
```powershell
psql -U postgres -c "CREATE DATABASE busiada_boarding;"
```

### ❌ "relation does not exist"
**Solution:** Migrations didn't run properly
```powershell
cd Busiada_Boarding
..\venv\Scripts\python.exe manage.py migrate
```

### ❌ "Admin login not working"
**Solution:** Admin user lost after migration (no worries, create new one)
```powershell
cd Busiada_Boarding
..\venv\Scripts\python.exe manage.py createsuperuser
```

---

## ✨ What Gets Migrated

✅ **Automatically transferred:**
- All database tables and schema
- Admin users (via backup restore)
- Site pages and content
- Page images and documents
- Inquiry submissions
- All custom data

⚠️ **Requires manual action:**
- Non-database files (media, static) - No action needed
- Environment variables - Already configured in settings.py

---

## 📊 Verification

After migration, verify everything works:

```powershell
cd Busiada_Boarding

# Test migrations
..\venv\Scripts\python.exe manage.py check
# Should show: System check identified no issues (0 silenced).

# Test admin login
..\venv\Scripts\python.exe manage.py runserver
# Visit http://localhost:8000/admin
```

---

## 🔐 Security Notes

For **production deployment** (not Windows dev machine):

1. **Never commit passwords to git:**
   ```python
   # Use environment variables instead
   PASSWORD = os.getenv('DB_PASSWORD')
   ```

2. **Use strong passwords:**
   ```powershell
   # Change default postgres password
   psql -U postgres -c "ALTER USER postgres PASSWORD 'SuperSecurePassword123!'"
   ```

3. **Restrict database access:**
   - Only allow local connections in production
   - Use SSL certificates for remote connections

---

## 📦 Rollback (If Needed)

If something goes wrong, you can revert to SQLite:

1. Restore settings.py to SQLite config
2. Copy old `db.sqlite3` (auto-backed up)
3. Run: `python manage.py migrate`

**But you won't need to - the migration is safe!**

---

## ✅ Quick Checklist

- [ ] PostgreSQL installed and running
- [ ] `busiada_boarding` database created
- [ ] `psycopg2-binary` pip package installed
- [ ] `config/settings.py` updated with correct password
- [ ] `migrate_to_postgres.py` script executed successfully
- [ ] Admin login works at `/admin`
- [ ] Homepage loads correctly
- [ ] Upload a test image to verify media handling

---

## 🎉 Success!

You now have:
- ✅ PostgreSQL production-ready database
- ✅ All data safely migrated
- ✅ Admin interface fully functional
- ✅ Ready for deployment to production servers

**Next step:** Consider Gunicorn + Nginx for production hosting!

---

## 📞 Need Help?

Check Django docs: https://docs.djangoproject.com/en/stable/ref/databases/  
PostgreSQL docs: https://www.postgresql.org/docs/
