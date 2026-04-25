#!/usr/bin/env python
"""Setup script for Influencer Affiliate Platform"""
import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a shell command"""
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0

def main():
    print("Setting up Influencer Affiliate Platform...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required")
        return 1
    
    # Setup backend
    print("\n[1/4] Setting up backend...")
    if not os.path.exists('venv'):
        run_command('python -m venv venv')
    
    # Activate venv and install requirements
    if sys.platform == 'win32':
        pip_cmd = 'venv\\Scripts\\pip'
        python_cmd = 'venv\\Scripts\\python'
    else:
        pip_cmd = 'venv/bin/pip'
        python_cmd = 'venv/bin/python'
    
    run_command(f'{pip_cmd} install -r requirements.txt')
    
    # Run migrations
    print("\n[2/4] Running database migrations...")
    os.chdir('backend')
    run_command(f'{python_cmd} manage.py migrate')
    
    # Create demo users
    print("\n[3/4] Creating demo users...")
    run_command(f'{python_cmd} manage.py shell -c "'
        'from django.contrib.auth import get_user_model; '
        'User = get_user_model(); '
        'User.objects.filter(email=\"admin@example.com\").exists() or '
        'User.objects.create_superuser(\"admin\", \"admin@example.com\", \"admin123\", role=\"admin\"); '
        'User.objects.filter(email=\"influencer@example.com\").exists() or '
        'User.objects.create_user(\"influencer\", \"influencer@example.com\", \"inf123\", role=\"influencer\"); '
        'print(\"Demo users created\")"'
    )
    
    os.chdir('..')
    
    # Setup frontend
    print("\n[4/4] Setting up frontend...")
    os.chdir('frontend')
    run_command('npm install')
    os.chdir('..')
    
    print("\n✅ Setup complete!")
    print("\nTo start the application:")
    print("  1. Backend: cd backend && ../venv/Scripts/python manage.py runserver")
    print("  2. Frontend: cd frontend && npm start")
    print("\nDemo credentials:")
    print("  Admin: admin@example.com / admin123")
    print("  Influencer: influencer@example.com / inf123")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
