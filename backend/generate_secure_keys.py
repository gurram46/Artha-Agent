#!/usr/bin/env python3
"""
Secure Key Generation Script for Artha AI
=========================================

Generates cryptographically secure keys and updates the .env file.

Usage:
    python generate_secure_keys.py [--backup] [--force]
    
    --backup: Create backup of existing .env file
    --force:  Overwrite existing keys without confirmation

Author: Artha AI Team
Version: 1.0
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from utils.security_utils import generate_production_keys, update_env_file, SecurityManager
except ImportError:
    print("❌ Error: Could not import security_utils. Make sure the utils directory exists.")
    sys.exit(1)

def backup_env_file(env_path: str) -> str:
    """Create backup of existing .env file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{env_path}.backup_{timestamp}"
        shutil.copy2(env_path, backup_path)
        print(f"📋 Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        raise

def validate_existing_keys(env_path: str) -> dict:
    """Validate existing keys in .env file"""
    weak_keys = {}
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        security_manager = SecurityManager()
        
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Check encryption keys
                if 'ENCRYPTION_KEY' in key or 'SECRET' in key:
                    if not security_manager.validate_key_strength(value):
                        weak_keys[key] = "Weak or default key detected"
                    elif value.count('A') > len(value) * 0.8:  # Mostly 'A' characters (default)
                        weak_keys[key] = "Default key detected"
        
        return weak_keys
    except Exception as e:
        print(f"⚠️  Warning: Could not validate existing keys: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description='Generate secure keys for Artha AI')
    parser.add_argument('--backup', action='store_true', help='Create backup of existing .env file')
    parser.add_argument('--force', action='store_true', help='Overwrite existing keys without confirmation')
    parser.add_argument('--env-path', default='.env', help='Path to .env file (default: .env)')
    
    args = parser.parse_args()
    
    # Determine .env file path
    env_path = Path(args.env_path)
    if not env_path.is_absolute():
        env_path = Path(__file__).parent / env_path
    
    env_path = str(env_path)
    
    print("🔐 Artha AI Secure Key Generator")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists(env_path):
        print(f"❌ Error: .env file not found at {env_path}")
        sys.exit(1)
    
    # Validate existing keys
    print("🔍 Validating existing keys...")
    weak_keys = validate_existing_keys(env_path)
    
    if weak_keys:
        print("⚠️  Weak or default keys detected:")
        for key, issue in weak_keys.items():
            print(f"  - {key}: {issue}")
    else:
        print("✅ No weak keys detected")
    
    # Ask for confirmation unless --force is used
    if not args.force:
        if weak_keys:
            response = input("\n🔄 Generate new secure keys? (y/N): ")
        else:
            response = input("\n🔄 All keys appear secure. Generate new keys anyway? (y/N): ")
        
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    
    try:
        # Create backup if requested
        if args.backup:
            backup_env_file(env_path)
        
        # Generate new keys
        print("\n🔐 Generating secure production keys...")
        new_keys = generate_production_keys()
        
        # Update .env file
        print(f"📝 Updating {env_path}...")
        update_env_file(env_path, new_keys)
        
        print("\n✅ Security keys updated successfully!")
        print("\n📋 Summary:")
        for key_name in new_keys.keys():
            print(f"  ✅ {key_name}: Updated")
        
        print("\n⚠️  IMPORTANT SECURITY NOTES:")
        print("  1. Restart your application to use the new keys")
        print("  2. Never commit these keys to version control")
        print("  3. Store backup keys securely")
        print("  4. Consider rotating keys every 30 days")
        
        if args.backup:
            print(f"  5. Backup saved for rollback if needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()