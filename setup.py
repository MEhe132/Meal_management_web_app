"""
Quick Start Setup Script
Run this to set up the application on first install
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and display status"""
    print(f"\n📦 {description}...")
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"✅ {description} completed!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {description} failed!")
        return False

def main():
    print("="*60)
    print("🏠 HOSTEL MEAL MANAGEMENT SYSTEM - SETUP")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher required!")
        return False
    
    print(f"\n✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment
    venv_name = 'venv'
    if not os.path.exists(venv_name):
        print(f"\n📁 Creating virtual environment '{venv_name}'...")
        if sys.platform == 'win32':
            run_command(f'python -m venv {venv_name}', 'Creating virtual environment')
        else:
            run_command(f'python3 -m venv {venv_name}', 'Creating virtual environment')
    else:
        print(f"\n✅ Virtual environment '{venv_name}' already exists")
    
    # Determine activation command based on OS
    if sys.platform == 'win32':
        activate_cmd = f'{venv_name}\\Scripts\\activate.bat && '
        pip_cmd = f'{venv_name}\\Scripts\\pip'
    else:
        activate_cmd = f'source {venv_name}/bin/activate && '
        pip_cmd = f'{venv_name}/bin/pip'
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    install_cmd = f'{pip_cmd} install -r requirements.txt'
    if run_command(install_cmd, 'Installing dependencies'):
        print("✅ All dependencies installed!")
    else:
        print("⚠️  Failed to install dependencies. Try manually: pip install -r requirements.txt")
    
    # Initialize demo data
    print("\n🗄️ Initializing demo data...")
    if sys.platform == 'win32':
        init_cmd = f'{venv_name}\\Scripts\\python init_demo.py'
    else:
        init_cmd = f'source {venv_name}/bin/activate && python init_demo.py'
    
    run_command(init_cmd, 'Initializing demo data')
    
    # Print success message
    print("\n" + "="*60)
    print("✨ SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\n🚀 To start the application:\n")
    if sys.platform == 'win32':
        print(f"1. Activate virtual environment: {venv_name}\\Scripts\\activate")
    else:
        print(f"1. Activate virtual environment: source {venv_name}/bin/activate")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5900")
    
    print("\n📝 Default Credentials:")
    print("   Manager: manager@example.com / password")
    print("   Member: mehedi@example.com / password")
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
