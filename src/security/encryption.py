"""
Encryption utilities for AI Call Secretary.
Provides functionality for encrypting sensitive data like passwords and PII.
"""
import os
import base64
import hashlib
import logging
from typing import Dict, Any, Union, Optional
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key,
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)

from src.security_config import security_config

# Initialize logging
logger = logging.getLogger(__name__)

class EncryptionService:
    """
    Service for encrypting and decrypting sensitive data.
    Provides both symmetric and asymmetric encryption capabilities.
    """
    
    def __init__(self, key_path: Optional[str] = None):
        """
        Initialize the encryption service.
        
        Args:
            key_path: Path to store encryption keys. If None, will use 'keys/'
        """
        self.key_path = key_path or "keys"
        
        # Create keys directory if it doesn't exist
        os.makedirs(self.key_path, exist_ok=True)
        
        # Initialize Fernet key for symmetric encryption
        self.fernet_key = self._load_or_generate_fernet_key()
        self.fernet = Fernet(self.fernet_key)
        
        # Initialize RSA keys for asymmetric encryption
        self.rsa_private_key, self.rsa_public_key = self._load_or_generate_rsa_keys()
        
        logger.info("Encryption service initialized")
    
    def _load_or_generate_fernet_key(self) -> bytes:
        """
        Load Fernet key from file or generate a new one.
        
        Returns:
            Fernet key as bytes
        """
        fernet_key_path = os.path.join(self.key_path, "fernet.key")
        
        # Check for environment variable override
        env_key = os.environ.get("ENCRYPTION_KEY")
        if env_key:
            try:
                # Try to use the environment variable as a base64 key
                key = base64.urlsafe_b64decode(env_key)
                if len(key) == 32:  # Valid Fernet key
                    return env_key.encode()
            except Exception:
                logger.warning("Invalid encryption key in environment variable. Falling back to file.")
        
        # Try to load from file
        try:
            if os.path.exists(fernet_key_path):
                with open(fernet_key_path, "rb") as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Error loading Fernet key: {str(e)}")
        
        # Generate new key
        key = Fernet.generate_key()
        
        # Save to file with restricted permissions
        try:
            with open(fernet_key_path, "wb") as f:
                f.write(key)
            
            # Set permissions to 600 (owner read/write only)
            os.chmod(fernet_key_path, 0o600)
        except Exception as e:
            logger.warning(f"Error saving Fernet key: {str(e)}")
        
        return key
    
    def _load_or_generate_rsa_keys(self) -> tuple:
        """
        Load RSA keys from files or generate new ones.
        
        Returns:
            Tuple of (private_key, public_key)
        """
        private_key_path = os.path.join(self.key_path, "rsa_private.pem")
        public_key_path = os.path.join(self.key_path, "rsa_public.pem")
        
        # Try to load keys from files
        try:
            if os.path.exists(private_key_path) and os.path.exists(public_key_path):
                with open(private_key_path, "rb") as f:
                    private_key = load_pem_private_key(
                        f.read(),
                        password=None,
                        backend=default_backend()
                    )
                
                with open(public_key_path, "rb") as f:
                    public_key = load_pem_public_key(
                        f.read(),
                        backend=default_backend()
                    )
                
                return private_key, public_key
        except Exception as e:
            logger.warning(f"Error loading RSA keys: {str(e)}")
        
        # Generate new keys
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Save to files with restricted permissions
        try:
            # Save private key
            private_pem = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )
            with open(private_key_path, "wb") as f:
                f.write(private_pem)
            
            # Set permissions to 600 (owner read/write only)
            os.chmod(private_key_path, 0o600)
            
            # Save public key
            public_pem = public_key.public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
            with open(public_key_path, "wb") as f:
                f.write(public_pem)
        except Exception as e:
            logger.warning(f"Error saving RSA keys: {str(e)}")
        
        return private_key, public_key
    
    def encrypt_symmetric(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data using symmetric encryption (Fernet).
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Base64-encoded encrypted data
        """
        try:
            # Convert to bytes if string
            if isinstance(data, str):
                data = data.encode()
            
            # Encrypt
            encrypted = self.fernet.encrypt(data)
            
            # Return as base64 string
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}", exc_info=True)
            raise
    
    def decrypt_symmetric(self, encrypted_data: Union[str, bytes]) -> bytes:
        """
        Decrypt data using symmetric encryption (Fernet).
        
        Args:
            encrypted_data: Encrypted data (base64 string or bytes)
            
        Returns:
            Decrypted data as bytes
        """
        try:
            # Convert from base64 string if needed
            if isinstance(encrypted_data, str):
                encrypted_data = base64.urlsafe_b64decode(encrypted_data)
            
            # Decrypt
            return self.fernet.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}", exc_info=True)
            raise
    
    def encrypt_asymmetric(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data using asymmetric encryption (RSA).
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Base64-encoded encrypted data
        """
        try:
            # Convert to bytes if string
            if isinstance(data, str):
                data = data.encode()
            
            # RSA can only encrypt small amounts of data, so we use hybrid encryption
            # for larger data by generating a random key, encrypting the data with it,
            # and then encrypting the key with RSA
            
            # Generate random Fernet key
            random_key = Fernet.generate_key()
            random_fernet = Fernet(random_key)
            
            # Encrypt data with random key
            encrypted_data = random_fernet.encrypt(data)
            
            # Encrypt random key with RSA
            encrypted_key = self.rsa_public_key.encrypt(
                random_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Combine encrypted key and data
            result = {
                "key": base64.b64encode(encrypted_key).decode(),
                "data": base64.b64encode(encrypted_data).decode()
            }
            
            # Return as JSON string
            return base64.b64encode(str(result).encode()).decode()
        except Exception as e:
            logger.error(f"Error encrypting data with RSA: {str(e)}", exc_info=True)
            raise
    
    def decrypt_asymmetric(self, encrypted_data: str) -> bytes:
        """
        Decrypt data using asymmetric encryption (RSA).
        
        Args:
            encrypted_data: Encrypted data as base64 string
            
        Returns:
            Decrypted data as bytes
        """
        try:
            # Parse encrypted data
            result = eval(base64.b64decode(encrypted_data).decode())
            encrypted_key = base64.b64decode(result["key"])
            encrypted_data = base64.b64decode(result["data"])
            
            # Decrypt random key with RSA private key
            random_key = self.rsa_private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Create Fernet instance with decrypted key
            random_fernet = Fernet(random_key)
            
            # Decrypt data
            return random_fernet.decrypt(encrypted_data)
        except Exception as e:
            logger.error(f"Error decrypting data with RSA: {str(e)}", exc_info=True)
            raise
    
    def encrypt_dict(self, data: Dict[str, Any], sensitive_fields: Optional[list] = None) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in a dictionary.
        
        Args:
            data: Dictionary to encrypt
            sensitive_fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        if sensitive_fields is None:
            sensitive_fields = security_config.logging.sensitive_fields
        
        result = {}
        for key, value in data.items():
            if key.lower() in [field.lower() for field in sensitive_fields]:
                # Encrypt sensitive field
                result[key] = {"__encrypted": self.encrypt_symmetric(str(value))}
            elif isinstance(value, dict):
                # Recursively encrypt nested dictionaries
                result[key] = self.encrypt_dict(value, sensitive_fields)
            elif isinstance(value, list):
                # Recursively encrypt lists of dictionaries
                result[key] = [
                    self.encrypt_dict(item, sensitive_fields) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # Keep non-sensitive fields as-is
                result[key] = value
        
        return result
    
    def decrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in a dictionary.
        
        Args:
            data: Dictionary with encrypted fields
            
        Returns:
            Dictionary with decrypted fields
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                if "__encrypted" in value:
                    # Decrypt encrypted field
                    result[key] = self.decrypt_symmetric(value["__encrypted"]).decode()
                else:
                    # Recursively decrypt nested dictionaries
                    result[key] = self.decrypt_dict(value)
            elif isinstance(value, list):
                # Recursively decrypt lists of dictionaries
                result[key] = [
                    self.decrypt_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # Keep non-encrypted fields as-is
                result[key] = value
        
        return result
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Hash a password using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Salt to use (generated if None)
            
        Returns:
            Tuple of (hash, salt)
        """
        # Generate random salt if not provided
        if salt is None:
            salt = os.urandom(16)
        
        # Create PBKDF2 instance
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        # Hash password
        password_hash = kdf.derive(password.encode())
        
        return password_hash, salt
    
    def verify_password(self, password: str, password_hash: bytes, salt: bytes) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Password to verify
            password_hash: Hash to verify against
            salt: Salt used to generate the hash
            
        Returns:
            True if password matches hash, False otherwise
        """
        # Create PBKDF2 instance
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        try:
            # Verify password
            kdf.verify(password.encode(), password_hash)
            return True
        except Exception:
            return False
    
    def get_public_key_pem(self) -> str:
        """
        Get the RSA public key in PEM format.
        
        Returns:
            Public key in PEM format
        """
        return self.rsa_public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode()

# Create global encryption service instance
encryption_service = EncryptionService()