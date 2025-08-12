"""
Artha AI - Encryption Utilities
===============================

AES-256 encryption utilities for secure financial data caching.
Provides high-security encryption with proper key management.
"""

import os
import base64
import json
import hashlib
from typing import Any, Dict, Optional, Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
from pathlib import Path
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

logger = logging.getLogger(__name__)

class EncryptionManager:
    """
    AES-256 encryption manager for secure data storage
    
    Features:
    - AES-256-CBC and AES-256-GCM encryption modes
    - Secure key derivation
    - Data integrity verification
    - Email hashing for privacy
    """
    
    def __init__(self):
        self.key = self._get_encryption_key()
        self.algorithm = "AES-256-CBC"
        
    def _get_encryption_key(self) -> bytes:
        """Get encryption key from environment variable"""
        key_string = os.getenv("ARTHA_ENCRYPTION_KEY")
        if not key_string:
            raise ValueError("ARTHA_ENCRYPTION_KEY environment variable not set")
        
        try:
            # Try to decode as base64 first (new format)
            try:
                key = base64.urlsafe_b64decode(key_string + '==')  # Add padding if needed
            except:
                # Fallback to regular base64 (old format)
                key = base64.b64decode(key_string)
            
            # Ensure key is 32 bytes for AES-256
            if len(key) < 32:
                # Derive a 32-byte key using PBKDF2
                key = PBKDF2(key_string, b'artha_salt', 32, count=100000)
            elif len(key) > 32:
                # Truncate to 32 bytes
                key = key[:32]
                
            return key
        except Exception as e:
            raise ValueError(f"Invalid encryption key format: {e}")
    
    def hash_user_email(self, email: str) -> str:
        """
        Create a secure hash of user email for database storage
        
        Args:
            email: User email address
            
        Returns:
            SHA-256 hash of the email (hex encoded)
        """
        return hashlib.sha256(email.encode()).hexdigest()
    
    def encrypt_data(self, data: Any) -> Dict[str, str]:
        """
        Encrypt data using AES-256-CBC
        
        Args:
            data: Data to encrypt (will be JSON serialized)
            
        Returns:
            Dict containing encrypted data and metadata
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, default=str)
            data_bytes = json_data.encode('utf-8')
            
            # Generate random IV
            iv = get_random_bytes(16)
            
            # Create cipher and encrypt
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            padded_data = pad(data_bytes, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # Encode to base64 for storage
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            iv_b64 = base64.b64encode(iv).decode('utf-8')
            
            return {
                "encrypted_data": encrypted_b64,
                "iv": iv_b64,
                "algorithm": self.algorithm,
                "version": "1.0"
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_package: Dict[str, str]) -> Any:
        """
        Decrypt data using AES-256-CBC
        
        Args:
            encrypted_package: Dict containing encrypted data and metadata
            
        Returns:
            Decrypted data (original Python object)
        """
        try:
            # Extract components
            encrypted_b64 = encrypted_package["encrypted_data"]
            iv_b64 = encrypted_package["iv"]
            
            # Decode from base64
            encrypted_data = base64.b64decode(encrypted_b64)
            iv = base64.b64decode(iv_b64)
            
            # Create cipher and decrypt
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            padded_data = cipher.decrypt(encrypted_data)
            data_bytes = unpad(padded_data, AES.block_size)
            
            # Convert back to Python object
            json_data = data_bytes.decode('utf-8')
            return json.loads(json_data)
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_string(self, text: str) -> str:
        """
        Encrypt a simple string (for IDs, counts, etc.)
        
        Args:
            text: String to encrypt
            
        Returns:
            Base64 encoded encrypted string
        """
        try:
            data_bytes = text.encode('utf-8')
            iv = get_random_bytes(16)
            
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            padded_data = pad(data_bytes, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # Combine IV and encrypted data
            combined = iv + encrypted_data
            return base64.b64encode(combined).decode('utf-8')
            
        except Exception as e:
            logger.error(f"String encryption failed: {e}")
            raise
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Decrypt a simple string
        
        Args:
            encrypted_text: Base64 encoded encrypted string
            
        Returns:
            Decrypted string
        """
        try:
            combined = base64.b64decode(encrypted_text)
            iv = combined[:16]
            encrypted_data = combined[16:]
            
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            padded_data = cipher.decrypt(encrypted_data)
            data_bytes = unpad(padded_data, AES.block_size)
            
            return data_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"String decryption failed: {e}")
            raise
    
    def test_encryption(self) -> bool:
        """
        Test encryption/decryption functionality
        
        Returns:
            True if test passes, False otherwise
        """
        try:
            # Test data encryption
            test_data = {
                "test": "data",
                "number": 123,
                "array": [1, 2, 3],
                "nested": {"key": "value"}
            }
            
            encrypted = self.encrypt_data(test_data)
            decrypted = self.decrypt_data(encrypted)
            
            if decrypted != test_data:
                logger.error("Data encryption test failed: data mismatch")
                return False
            
            # Test string encryption
            test_string = "test_string_123"
            encrypted_string = self.encrypt_string(test_string)
            decrypted_string = self.decrypt_string(encrypted_string)
            
            if decrypted_string != test_string:
                logger.error("String encryption test failed: string mismatch")
                return False
            
            logger.info("✅ Encryption tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Encryption test failed: {e}")
            return False
    
    def encrypt_data_gcm(self, data: Any) -> Dict[str, str]:
        """
        Encrypt data using AES-256-GCM for enhanced security
        
        Args:
            data: Data to encrypt (will be JSON serialized)
            
        Returns:
            Dict containing encrypted data and metadata
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, default=str, ensure_ascii=False)
            data_bytes = json_data.encode('utf-8')
            
            # Generate random nonce for GCM mode
            nonce = get_random_bytes(12)  # 96-bit nonce for GCM
            
            # Create cipher
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            
            # Encrypt and get authentication tag
            ciphertext, auth_tag = cipher.encrypt_and_digest(data_bytes)
            
            # Encode everything as base64 for storage
            return {
                'encrypted_data': base64.b64encode(ciphertext).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8'),
                'auth_tag': base64.b64encode(auth_tag).decode('utf-8'),
                'algorithm': 'AES-256-GCM',
                'version': '2.0'
            }
            
        except Exception as e:
            logger.error(f"GCM encryption failed: {e}")
            raise
    
    def decrypt_data_gcm(self, encrypted_package: Dict[str, str]) -> Any:
        """
        Decrypt data using AES-256-GCM
        
        Args:
            encrypted_package: Dict containing encrypted data and metadata
            
        Returns:
            Decrypted data (original Python object)
        """
        try:
            # Decode base64 data
            ciphertext = base64.b64decode(encrypted_package['encrypted_data'])
            nonce = base64.b64decode(encrypted_package['nonce'])
            auth_tag = base64.b64decode(encrypted_package['auth_tag'])
            
            # Create cipher with the same nonce
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            
            # Decrypt and verify authentication tag
            decrypted_bytes = cipher.decrypt_and_verify(ciphertext, auth_tag)
            
            # Convert back to dictionary
            json_string = decrypted_bytes.decode('utf-8')
            return json.loads(json_string)
            
        except Exception as e:
            logger.error(f"GCM decryption failed: {e}")
            raise
    
    def encrypt_for_database(self, data: Any) -> Tuple[str, str, str]:
        """
        Encrypt data and return components for database storage
        
        Args:
            data: Financial data to encrypt
            
        Returns:
            Tuple of (encrypted_data, nonce, auth_tag) as base64 strings
        """
        encrypted = self.encrypt_data_gcm(data)
        return (
            encrypted['encrypted_data'],
            encrypted['nonce'],
            encrypted['auth_tag']
        )
    
    def decrypt_from_database(self, encrypted_data: str, nonce: str, auth_tag: str) -> Any:
        """
        Decrypt data from database storage format
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            nonce: Base64 encoded nonce
            auth_tag: Base64 encoded authentication tag
            
        Returns:
            Original financial data
        """
        encrypted_package = {
            'encrypted_data': encrypted_data,
            'nonce': nonce,
            'auth_tag': auth_tag,
            'algorithm': 'AES-256-GCM',
            'version': '2.0'
        }
        return self.decrypt_data_gcm(encrypted_package)

def generate_encryption_key() -> str:
    """
    Generate a new secure encryption key
    
    Returns:
        Base64url encoded 32-byte encryption key
    """
    key_bytes = get_random_bytes(32)  # 256 bits
    return base64.urlsafe_b64encode(key_bytes).decode('utf-8').rstrip('=')

def test_encryption_system():
    """Test the encryption system with sample data"""
    print("🔐 Testing encryption system...")
    
    try:
        manager = EncryptionManager()
        
        # Test data
        test_data = {
            "user_id": "test@example.com",
            "financial_data": {
                "accounts": [
                    {"name": "Savings", "balance": 10000.50},
                    {"name": "Checking", "balance": 2500.75}
                ],
                "investments": {
                    "stocks": 15000.00,
                    "bonds": 5000.00
                },
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
        
        print(f"   Original data size: {len(json.dumps(test_data))} bytes")
        
        # Test GCM encryption
        encrypted = manager.encrypt_data_gcm(test_data)
        print(f"   Encrypted data size: {len(encrypted['encrypted_data'])} bytes")
        
        # Test decryption
        decrypted = manager.decrypt_data_gcm(encrypted)
        
        # Verify integrity
        if decrypted == test_data:
            print("   ✅ GCM encryption/decryption successful")
            print("   ✅ Data integrity verified")
            
            # Test email hashing
            email_hash = manager.hash_user_email("test@example.com")
            print(f"   ✅ Email hash: {email_hash[:16]}...")
            
            # Test database format
            db_encrypted, db_nonce, db_tag = manager.encrypt_for_database(test_data)
            db_decrypted = manager.decrypt_from_database(db_encrypted, db_nonce, db_tag)
            
            if db_decrypted == test_data:
                print("   ✅ Database format encryption successful")
                return True
            else:
                print("   ❌ Database format test failed")
                return False
        else:
            print("   ❌ Data integrity check failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Encryption test failed: {e}")
        return False

# Global encryption instance
encryption = EncryptionManager()

# Alias for backward compatibility
EncryptionHelper = EncryptionManager

if __name__ == "__main__":
    # Direct execution for testing
    test_encryption_system()