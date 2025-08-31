#!/usr/bin/env python3
"""
Security Utilities for Artha AI
===============================

Provides secure key generation, encryption utilities, and security helpers.

Author: Artha AI Team
Version: 1.0
"""

import os
import secrets
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Manages encryption keys and security operations"""
    
    def __init__(self):
        self.key_rotation_interval = timedelta(days=30)  # Rotate keys every 30 days
        self.key_history: Dict[str, Any] = {}
    
    @staticmethod
    def generate_secure_key(length: int = 32) -> str:
        """Generate a cryptographically secure random key"""
        try:
            # Generate random bytes
            key_bytes = secrets.token_bytes(length)
            # Encode as base64 for storage
            return base64.urlsafe_b64encode(key_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate secure key: {e}")
            raise
    
    @staticmethod
    def generate_fernet_key() -> str:
        """Generate a Fernet-compatible encryption key"""
        try:
            return Fernet.generate_key().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate Fernet key: {e}")
            raise
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,  # OWASP recommended minimum
            )
            return kdf.derive(password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to derive key from password: {e}")
            raise
    
    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """Generate a cryptographically secure salt"""
        try:
            salt_bytes = secrets.token_bytes(length)
            return base64.urlsafe_b64encode(salt_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate salt: {e}")
            raise
    
    def should_rotate_key(self, key_created_at: datetime) -> bool:
        """Check if a key should be rotated based on age"""
        return datetime.now() - key_created_at > self.key_rotation_interval
    
    def create_key_metadata(self, key_type: str) -> Dict[str, Any]:
        """Create metadata for a generated key"""
        return {
            'type': key_type,
            'created_at': datetime.now().isoformat(),
            'rotation_due': (datetime.now() + self.key_rotation_interval).isoformat(),
            'version': 1
        }
    
    @staticmethod
    def validate_key_strength(key: str, min_length: int = 32) -> bool:
        """Validate that a key meets minimum security requirements"""
        try:
            # Check minimum length
            if len(key) < min_length:
                return False
            
            # Check for base64 encoding
            try:
                base64.urlsafe_b64decode(key.encode('utf-8'))
            except Exception:
                return False
            
            # Check entropy (basic check)
            unique_chars = len(set(key))
            if unique_chars < min_length // 4:  # At least 25% unique characters
                return False
            
            return True
        except Exception as e:
            logger.error(f"Key validation failed: {e}")
            return False
    
    @staticmethod
    def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
        """Hash sensitive data with optional salt"""
        try:
            if salt is None:
                salt = SecurityManager.generate_salt()
            
            # Combine data and salt
            combined = f"{data}{salt}"
            
            # Create SHA-256 hash
            hash_obj = hashlib.sha256(combined.encode('utf-8'))
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash sensitive data: {e}")
            raise

def generate_production_keys() -> Dict[str, str]:
    """Generate all required production keys"""
    try:
        security_manager = SecurityManager()
        
        keys = {
            'ENCRYPTION_KEY': security_manager.generate_secure_key(44),  # 44 chars for base64 32-byte key
            'ARTHA_ENCRYPTION_KEY': security_manager.generate_fernet_key(),
            'CACHE_ENCRYPTION_SALT': security_manager.generate_salt(24),
            'JWT_SECRET_KEY': security_manager.generate_secure_key(64),  # Longer for JWT
            'SESSION_SECRET_KEY': security_manager.generate_secure_key(32),
        }
        
        # Log key generation (without exposing actual keys)
        logger.info("🔐 Generated secure production keys:")
        for key_name in keys.keys():
            logger.info(f"  ✅ {key_name}: Generated ({len(keys[key_name])} chars)")
        
        return keys
    except Exception as e:
        logger.error(f"Failed to generate production keys: {e}")
        raise

def update_env_file(env_path: str, new_keys: Dict[str, str]) -> None:
    """Update .env file with new secure keys"""
    try:
        # Read current .env file
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update keys in memory
        updated_lines = []
        keys_updated = set()
        
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                
                if key in new_keys:
                    updated_lines.append(f"{key}={new_keys[key]}\n")
                    keys_updated.add(key)
                else:
                    updated_lines.append(line + '\n')
            else:
                updated_lines.append(line + '\n')
        
        # Add any new keys that weren't in the original file
        for key, value in new_keys.items():
            if key not in keys_updated:
                updated_lines.append(f"\n# Security Key (Generated: {datetime.now().isoformat()})\n")
                updated_lines.append(f"{key}={value}\n")
        
        # Write updated .env file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        logger.info(f"🔐 Updated {len(new_keys)} security keys in {env_path}")
        
    except Exception as e:
        logger.error(f"Failed to update .env file: {e}")
        raise

if __name__ == "__main__":
    # Generate and display new keys for manual update
    print("🔐 Generating secure production keys...")
    keys = generate_production_keys()
    
    print("\n📋 Copy these keys to your .env file:")
    print("=" * 50)
    for key, value in keys.items():
        print(f"{key}={value}")
    print("=" * 50)
    print("\n⚠️  IMPORTANT: Store these keys securely and never commit them to version control!")