"""
Data Encryption Service
Advanced data encryption with AES-256, RSA, and hybrid encryption
"""
import asyncio
import json
import time
import secrets
import hashlib
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ...Redis.client import get_redis_client


class EncryptionAlgorithm(Enum):
    """Encryption algorithm enumeration"""
    AES_256_GCM = "aes_256_gcm"
    RSA_4096 = "rsa_4096"
    HYBRID = "hybrid"  # AES for data + RSA for key


class KeyType(Enum):
    """Key type enumeration"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"


@dataclass
class EncryptionKey:
    """Encryption key storage"""
    key_id: str
    key_data: bytes
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    created_at: float
    expires_at: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EncryptedData:
    """Encrypted data container"""
    encrypted_data: bytes
    encryption_algorithm: EncryptionAlgorithm
    key_id: str
    nonce: Optional[bytes] = None
    additional_data: Optional[bytes] = None
    timestamp: float = time.time()


class DataEncryptionService:
    """Advanced data encryption service with multiple algorithms"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.encryption_prefix = "data_encryption"

        # Encryption statistics
        self.stats = {
            "keys_generated": 0,
            "data_encrypted": 0,
            "data_decrypted": 0,
            "errors": 0
        }

        # Key rotation settings
        self.default_key_rotation_days = 90

    async def generate_key(
        self,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        key_rotation_days: int = 90
    ) -> str:
        """Generate encryption key"""
        try:
            key_id = f"key_{int(time.time() * 1000)}_{secrets.token_hex(8)}"

            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                key_data = AESGCM.generate_key(bit_length=256)
                key_type = KeyType.SYMMETRIC
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                )
                key_data = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                key_type = KeyType.ASYMMETRIC_PRIVATE
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")

            # Create key object
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_data=key_data,
                key_type=key_type,
                algorithm=algorithm,
                created_at=time.time(),
                expires_at=time.time() + (key_rotation_days * 24 * 60 * 60) if key_rotation_days > 0 else None
            )

            # Store key in Redis
            await self.redis_client.setex(
                f"{self.encryption_prefix}:key:{key_id}",
                key_rotation_days * 24 * 60 * 60 if key_rotation_days > 0 else 86400 * 365,  # 1 year default
                json.dumps({
                    "key_id": encryption_key.key_id,
                    "key_data": encryption_key.key_data.hex(),
                    "key_type": encryption_key.key_type.value,
                    "algorithm": encryption_key.algorithm.value,
                    "created_at": encryption_key.created_at,
                    "expires_at": encryption_key.expires_at,
                    "metadata": encryption_key.metadata
                }, default=str)
            )

            self.stats["keys_generated"] += 1

            return key_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Key generation error: {e}")
            raise

    async def encrypt_data(
        self,
        data: bytes,
        key_id: str,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        additional_data: Optional[bytes] = None
    ) -> EncryptedData:
        """Encrypt data with specified key and algorithm"""
        try:
            # Get key from Redis
            key_data = await self.redis_client.get(f"{self.encryption_prefix}:key:{key_id}")
            if not key_data:
                raise ValueError(f"Key not found: {key_id}")

            key_info = json.loads(key_data)
            key_bytes = bytes.fromhex(key_info["key_data"])

            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                # AES-GCM encryption
                aesgcm = AESGCM(key_bytes)
                nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
                encrypted_data = aesgcm.encrypt(nonce, data, additional_data)
                
                result = EncryptedData(
                    encrypted_data=encrypted_data,
                    encryption_algorithm=algorithm,
                    key_id=key_id,
                    nonce=nonce,
                    additional_data=additional_data
                )

            elif algorithm == EncryptionAlgorithm.RSA_4096:
                # RSA encryption
                private_key = serialization.load_pem_private_key(
                    key_bytes,
                    password=None,
                )
                public_key = private_key.public_key()
                
                encrypted_data = public_key.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                result = EncryptedData(
                    encrypted_data=encrypted_data,
                    encryption_algorithm=algorithm,
                    key_id=key_id
                )

            elif algorithm == EncryptionAlgorithm.HYBRID:
                # Hybrid encryption: AES for data + RSA for key
                # Generate random AES key
                aes_key = AESGCM.generate_key(bit_length=256)
                
                # Encrypt data with AES
                aesgcm = AESGCM(aes_key)
                nonce = secrets.token_bytes(12)
                encrypted_data = aesgcm.encrypt(nonce, data, additional_data)
                
                # Encrypt AES key with RSA
                private_key = serialization.load_pem_private_key(
                    key_bytes,
                    password=None,
                )
                public_key = private_key.public_key()
                
                encrypted_key = public_key.encrypt(
                    aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Combine encrypted data and encrypted key
                combined_data = encrypted_key + b"::SPLIT::" + encrypted_data
                
                result = EncryptedData(
                    encrypted_data=combined_data,
                    encryption_algorithm=algorithm,
                    key_id=key_id,
                    nonce=nonce,
                    additional_data=additional_data
                )

            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")

            self.stats["data_encrypted"] += 1

            return result

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Data encryption error: {e}")
            raise

    async def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data with specified key"""
        try:
            # Get key from Redis
            key_data = await self.redis_client.get(f"{self.encryption_prefix}:key:{encrypted_data.key_id}")
            if not key_data:
                raise ValueError(f"Key not found: {encrypted_data.key_id}")

            key_info = json.loads(key_data)
            key_bytes = bytes.fromhex(key_info["key_data"])

            if encrypted_data.encryption_algorithm == EncryptionAlgorithm.AES_256_GCM:
                # AES-GCM decryption
                aesgcm = AESGCM(key_bytes)
                decrypted_data = aesgcm.decrypt(
                    encrypted_data.nonce,
                    encrypted_data.encrypted_data,
                    encrypted_data.additional_data
                )

            elif encrypted_data.encryption_algorithm == EncryptionAlgorithm.RSA_4096:
                # RSA decryption
                private_key = serialization.load_pem_private_key(
                    key_bytes,
                    password=None,
                )
                
                decrypted_data = private_key.decrypt(
                    encrypted_data.encrypted_data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

            elif encrypted_data.encryption_algorithm == EncryptionAlgorithm.HYBRID:
                # Hybrid decryption
                # Split combined data
                parts = encrypted_data.encrypted_data.split(b"::SPLIT::")
                if len(parts) != 2:
                    raise ValueError("Invalid hybrid encrypted data format")
                
                encrypted_key, encrypted_data_bytes = parts
                
                # Decrypt AES key with RSA
                private_key = serialization.load_pem_private_key(
                    key_bytes,
                    password=None,
                )
                
                aes_key = private_key.decrypt(
                    encrypted_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Decrypt data with AES
                aesgcm = AESGCM(aes_key)
                decrypted_data = aesgcm.decrypt(
                    encrypted_data.nonce,
                    encrypted_data_bytes,
                    encrypted_data.additional_data
                )

            else:
                raise ValueError(f"Unsupported algorithm: {encrypted_data.encryption_algorithm}")

            self.stats["data_decrypted"] += 1

            return decrypted_data

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Data decryption error: {e}")
            raise

    async def rotate_key(self, old_key_id: str) -> str:
        """Rotate encryption key"""
        try:
            # Get old key info
            old_key_data = await self.redis_client.get(f"{self.encryption_prefix}:key:{old_key_id}")
            if not old_key_data:
                raise ValueError(f"Old key not found: {old_key_id}")

            old_key_info = json.loads(old_key_data)
            
            # Generate new key with same algorithm
            new_key_id = await self.generate_key(
                algorithm=EncryptionAlgorithm(old_key_info["algorithm"])
            )

            # Mark old key as rotated
            old_key_info["rotated_at"] = time.time()
            old_key_info["new_key_id"] = new_key_id
            
            await self.redis_client.setex(
                f"{self.encryption_prefix}:key:{old_key_id}",
                86400 * 30,  # Keep rotated key for 30 days
                json.dumps(old_key_info, default=str)
            )

            return new_key_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Key rotation error: {e}")
            raise

    async def get_encryption_statistics(self) -> Dict[str, Any]:
        """Get encryption service statistics"""
        try:
            return {
                "encryption_stats": self.stats.copy(),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global data encryption service instance
data_encryption = DataEncryptionService()