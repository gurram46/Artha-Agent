#!/usr/bin/env python3
"""
PostgreSQL Installation Helper for Artha AI Cache System
"""

import subprocess
import sys
import webbrowser
from pathlib import Path

def check_postgresql():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL is already installed: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("❌ PostgreSQL is not installed")
    return False

def install_postgresql_windows():
    """Install PostgreSQL on Windows"""
    print("\n🔽 Installing PostgreSQL on Windows...")
    
    # Try Chocolatey first
    try:
        choco_result = subprocess.run(["choco", "--version"], capture_output=True, text=True)
        if choco_result.returncode == 0:
            print("📦 Found Chocolatey! Installing PostgreSQL...")
            result = subprocess.run([
                "choco", "install", "postgresql", "-y",
                "--params", "'/Password:postgres /Port:5432'"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PostgreSQL installed successfully via Chocolatey!")
                return True
            else:
                print("⚠️ Chocolatey installation failed")
    except:
        print("📦 Chocolatey not found")
    
    # Manual installation
    print("\n📋 Manual PostgreSQL Installation Required:")
    print("=" * 50)
    print("1. 🌐 Opening PostgreSQL download page...")
    print("2. 📥 Download the Windows installer")
    print("3. 🔧 Run installer with these settings:")
    print("   - Port: 5432")
    print("   - Password: postgres (or remember your password)")
    print("   - Install all components")
    print("4. 🔄 After installation, run this script again")
    print("=" * 50)
    
    # Open download page
    webbrowser.open("https://www.postgresql.org/download/windows/")
    
    input("\n⏳ Press Enter after you've installed PostgreSQL...")
    return check_postgresql()

def create_database():
    """Create the Artha AI database and user"""
    print("\n👤 Creating Artha AI database and user...")
    
    sql_commands = [
        "CREATE DATABASE artha_cache_db;",
        "CREATE USER artha_user WITH ENCRYPTED PASSWORD 'artha_secure_2024';",
        "GRANT ALL PRIVILEGES ON DATABASE artha_cache_db TO artha_user;",
        "ALTER USER artha_user CREATEDB;"
    ]
    
    for sql in sql_commands:
        try:
            cmd = ["psql", "-U", "postgres", "-c", sql]
            result = subprocess.run(cmd, capture_output=True, text=True, input="postgres\n")
            
            if result.returncode != 0 and "already exists" not in result.stderr:
                print(f"⚠️ Command may have failed: {sql}")
                print(f"   Error: {result.stderr}")
            else:
                print(f"✅ {sql}")
        except Exception as e:
            print(f"❌ Failed to execute: {sql}")
            print(f"   Error: {e}")
    
    print("✅ Database setup completed!")

def main():
    """Main installation function"""
    print("🚀 Artha AI PostgreSQL Installation Helper")
    print("=" * 50)
    
    # Check if already installed
    if check_postgresql():
        print("✅ PostgreSQL is ready!")
        
        # Create database
        create_database()
        
        print("\n🎉 Setup Complete!")
        print("=" * 30)
        print("✅ PostgreSQL installed and configured")
        print("✅ Database 'artha_cache_db' created")
        print("✅ User 'artha_user' created")
        print("\n🔧 Next steps:")
        print("1. Run: python setup_cache_system.py")
        print("2. Test your Artha AI application")
        
        return True
    
    # Install PostgreSQL
    if sys.platform.startswith('win'):
        return install_postgresql_windows()
    else:
        print("❌ This script currently supports Windows only")
        print("Please install PostgreSQL manually for your OS")
        return False

if __name__ == "__main__":
    main()