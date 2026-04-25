@echo off
echo ==========================================
echo Influencer Affiliate Platform - Quick Start
echo ==========================================
echo.

if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/3] Virtual environment already exists
)

echo.
echo [2/3] Installing dependencies...
venv\Scripts\pip install -r requirements.txt

echo.
echo [3/3] Running migrations...
cd backend
..\venv\Scripts\python manage.py migrate

REM Create demo data
echo.
echo Creating demo users...
..\venv\Scripts\python manage.py shell -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from core.models import Influencer
User = get_user_model()

# Create admin
if not User.objects.filter(email='admin@example.com').exists():
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')
    print('Admin created: admin@example.com')

# Create influencer
if not User.objects.filter(email='influencer@example.com').exists():
    user = User.objects.create_user('influencer1', 'influencer@example.com', 'inf123', role='influencer')
    Influencer.objects.create(user=user, bio='Demo influencer account')
    print('Influencer created: influencer@example.com')

# Create finance user
if not User.objects.filter(email='finance@example.com').exists():
    User.objects.create_user('finance', 'finance@example.com', 'fin123', role='finance')
    print('Finance user created: finance@example.com')

print('Demo users created successfully!')
"

cd ..

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To start the application:
echo.
echo 1. Start Backend (run in new terminal):
echo    cd backend ^&^& ..\venv\Scripts\python manage.py runserver
echo.
echo 2. Start Frontend (run in new terminal):
echo    cd frontend ^&^& npm install ^&^& npm start
echo.
echo Demo Credentials:
echo   Admin:      admin@example.com / admin123
echo   Influencer: influencer@example.com / inf123
echo   Finance:    finance@example.com / fin123
echo.
echo ==========================================

pause
