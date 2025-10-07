"""
Biometric Authentication Service
Advanced biometric authentication with fingerprint, face, and voice recognition
"""
import asyncio
import json
import time
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from ...Redis.client import get_redis_client


class BiometricType(Enum):
    """Biometric type enumeration"""
    FINGERPRINT = "fingerprint"
    FACE = "face"
    VOICE = "voice"
    IRIS = "iris"
    RETINA = "retina"


class BiometricSecurityLevel(Enum):
    """Biometric security level enumeration"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


@dataclass
class BiometricTemplate:
    """Biometric template storage"""
    user_id: str
    biometric_type: BiometricType
    template_data: str  # In production, this would be encrypted biometric data
    security_level: BiometricSecurityLevel
    created_at: float
    last_updated: float


@dataclass
class BiometricAuthenticationResult:
    """Biometric authentication result"""
    success: bool
    user_id: Optional[str]
    confidence_score: float
    security_level: BiometricSecurityLevel
    timestamp: float
    additional_data: Optional[Dict[str, Any]] = None


class BiometricAuthService:
    """Advanced biometric authentication service"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.biometric_prefix = "biometric_auth"

        # Biometric statistics
        self.stats = {
            "enrollments": 0,
            "auth_attempts": 0,
            "successful_auths": 0,
            "failed_auths": 0,
            "errors": 0
        }

        # Supported biometric algorithms (in production, would integrate with actual biometric SDKs)
        self.supported_algorithms = {
            BiometricType.FINGERPRINT: ["minutiae_matching", "pattern_matching"],
            BiometricType.FACE: ["eigenface", "fisherface", "deep_learning"],
            BiometricType.VOICE: ["mfcc", "spectral_features", "deep_learning"],
            BiometricType.IRIS: ["gabor_filter", "deep_learning"],
            BiometricType.RETINA: ["blood_vessel_pattern", "deep_learning"]
        }

    async def enroll_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        biometric_data: Any,
        security_level: BiometricSecurityLevel = BiometricSecurityLevel.HIGH
    ) -> bool:
        """Enroll user biometric data"""
        try:
            # Process biometric data (in production, would use actual biometric processing)
            # For demo, we'll just hash the data
            template_data = hashlib.sha256(str(biometric_data).encode()).hexdigest()

            # Create biometric template
            template = BiometricTemplate(
                user_id=user_id,
                biometric_type=biometric_type,
                template_data=template_data,
                security_level=security_level,
                created_at=time.time(),
                last_updated=time.time()
            )

            # Store template in Redis
            await self.redis_client.setex(
                f"{self.biometric_prefix}:template:{user_id}:{biometric_type.value}",
                86400 * 365,  # 1 year
                json.dumps(asdict(template), default=str)
            )

            # Add to user's biometric types
            self.redis_client.sadd(
                f"{self.biometric_prefix}:user_biometrics:{user_id}",
                biometric_type.value
            )

            self.stats["enrollments"] += 1

            return True

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Biometric enrollment error: {e}")
            return False

    async def authenticate_biometric(
        self,
        biometric_type: BiometricType,
        biometric_data: Any,
        required_security_level: BiometricSecurityLevel = BiometricSecurityLevel.MEDIUM
    ) -> BiometricAuthenticationResult:
        """Authenticate user using biometric data"""
        try:
            self.stats["auth_attempts"] += 1

            # Process biometric data (in production, would use actual biometric matching)
            # For demo, we'll just hash the data
            input_template = hashlib.sha256(str(biometric_data).encode()).hexdigest()

            # Get all user templates for this biometric type
            pattern = f"{self.biometric_prefix}:template:*:{biometric_type.value}"
            template_keys = await self.redis_client.keys(pattern)

            # Compare with all templates
            best_match = None
            best_confidence = 0.0

            for template_key in template_keys:
                template_data = await self.redis_client.get(template_key)
                if template_data:
                    template = BiometricTemplate(**json.loads(template_data))
                    
                    # Check security level
                    if template.security_level.value < required_security_level.value:
                        continue

                    # Calculate similarity (in production, would use actual biometric matching algorithm)
                    # For demo, we'll use a simple string comparison
                    similarity = self.calculate_similarity(input_template, template.template_data)
                    
                    if similarity > best_confidence:
                        best_confidence = similarity
                        best_match = template

            # Determine authentication result based on confidence threshold
            confidence_threshold = 0.8  # 80% confidence required
            success = best_confidence >= confidence_threshold and best_match is not None

            if success:
                self.stats["successful_auths"] += 1
            else:
                self.stats["failed_auths"] += 1

            return BiometricAuthenticationResult(
                success=success,
                user_id=best_match.user_id if best_match else None,
                confidence_score=best_confidence,
                security_level=best_match.security_level if best_match else BiometricSecurityLevel.LOW,
                timestamp=time.time(),
                additional_data={
                    "biometric_type": biometric_type.value,
                    "templates_compared": len(template_keys)
                }
            )

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Biometric authentication error: {e}")
            return BiometricAuthenticationResult(
                success=False,
                user_id=None,
                confidence_score=0.0,
                security_level=BiometricSecurityLevel.LOW,
                timestamp=time.time(),
                additional_data={"error": str(e)}
            )

    def calculate_similarity(self, input_data: str, template_data: str) -> float:
        """Calculate similarity between input and template data"""
        # In production, this would use actual biometric matching algorithms
        # For demo, we'll use a simple character matching approach
        
        if len(input_data) != len(template_data):
            return 0.0

        matches = sum(1 for a, b in zip(input_data, template_data) if a == b)
        return matches / len(input_data)

    async def get_user_biometrics(self, user_id: str) -> List[BiometricType]:
        """Get list of biometric types enrolled for user"""
        try:
            biometric_types = await self.redis_client.smembers(f"{self.biometric_prefix}:user_biometrics:{user_id}")
            return [BiometricType(bt) for bt in biometric_types]
        except Exception as e:
            print(f"Get user biometrics error: {e}")
            return []

    async def remove_biometric(self, user_id: str, biometric_type: BiometricType) -> bool:
        """Remove user's biometric enrollment"""
        try:
            # Remove template
            await self.redis_client.delete(f"{self.biometric_prefix}:template:{user_id}:{biometric_type.value}")
            
            # Remove from user's biometric types
            self.redis_client.srem(f"{self.biometric_prefix}:user_biometrics:{user_id}", biometric_type.value)
            
            return True
        except Exception as e:
            print(f"Remove biometric error: {e}")
            return False

    async def update_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        biometric_data: Any,
        security_level: BiometricSecurityLevel = BiometricSecurityLevel.HIGH
    ) -> bool:
        """Update user's biometric enrollment"""
        try:
            # Process biometric data
            template_data = hashlib.sha256(str(biometric_data).encode()).hexdigest()

            # Update biometric template
            template = BiometricTemplate(
                user_id=user_id,
                biometric_type=biometric_type,
                template_data=template_data,
                security_level=security_level,
                created_at=time.time(),  # Keep original creation time
                last_updated=time.time()
            )

            # Store updated template in Redis
            await self.redis_client.setex(
                f"{self.biometric_prefix}:template:{user_id}:{biometric_type.value}",
                86400 * 365,  # 1 year
                json.dumps(asdict(template), default=str)
            )

            return True

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Biometric update error: {e}")
            return False

    async def get_biometric_statistics(self) -> Dict[str, Any]:
        """Get biometric authentication statistics"""
        try:
            # Get total enrolled users
            pattern = f"{self.biometric_prefix}:user_biometrics:*"
            user_keys = await self.redis_client.keys(pattern)
            
            # Get biometric distribution
            biometric_distribution = {}
            for user_key in user_keys:
                biometric_types = await self.redis_client.smembers(user_key)
                for bt in biometric_types:
                    biometric_distribution[bt] = biometric_distribution.get(bt, 0) + 1

            return {
                "biometric_stats": self.stats.copy(),
                "enrolled_users": len(user_keys),
                "biometric_distribution": biometric_distribution,
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global biometric authentication service instance
biometric_auth = BiometricAuthService()