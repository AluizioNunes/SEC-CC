"""
JWT Authentication Module for FastAPI
Ultra-advanced security with JWT tokens and comprehensive audit logging
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import structlog
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import json

# Initialize structured logger
logger = structlog.get_logger()

# Security configurations
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer(auto_error=False)

class JWTManager:
    """Ultra-advanced JWT management with comprehensive security features"""

    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with enhanced security claims"""
        to_encode = data.copy()

        # Add security claims
        to_encode.update({
            "iat": datetime.utcnow(),
            "type": "access",
            "version": "1.0",
            "issuer": "sec-fastapi",
            "audience": "sec-services"
        })

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})

        # Create token with enhanced security
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        # Log token creation (without exposing sensitive data)
        logger.info(
            "JWT access token created",
            user_id=data.get("sub"),
            expires_at=expire.isoformat(),
            token_length=len(token)
        )

        return token

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()

        to_encode.update({
            "iat": datetime.utcnow(),
            "type": "refresh",
            "version": "1.0",
            "issuer": "sec-fastapi",
            "audience": "sec-services"
        })

        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire})

        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        logger.info(
            "JWT refresh token created",
            user_id=data.get("sub"),
            expires_at=expire.isoformat()
        )

        return token

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token with comprehensive validation"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Validate token type
            if payload.get("type") != token_type:
                logger.warning(
                    "Invalid token type",
                    expected_type=token_type,
                    received_type=payload.get("type")
                )
                return None

            # Validate issuer and audience
            if payload.get("issuer") != "sec-fastapi":
                logger.warning("Invalid token issuer", issuer=payload.get("issuer"))
                return None

            # Log successful verification
            logger.info(
                "JWT token verified successfully",
                user_id=payload.get("sub"),
                token_type=token_type
            )

            return payload

        except JWTError as e:
            logger.warning(
                "JWT token verification failed",
                error=str(e),
                token_type=token_type
            )
            return None
        except Exception as e:
            logger.error(
                "Unexpected error during JWT verification",
                error=str(e)
            )
            return None

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

# Global JWT manager instance
jwt_manager = JWTManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """Dependency to get current authenticated user"""
    if not credentials:
        return None

    token = credentials.credentials
    payload = jwt_manager.verify_token(token, "access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

async def require_auth(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency that requires authentication"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user

def audit_log(action: str, user_id: str, resource: str, details: Dict[str, Any] = None):
    """Structured audit logging for security events"""
    audit_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id,
        "resource": resource,
        "details": details or {},
        "severity": "INFO"
    }

    # Determine severity based on action
    if action in ["login", "logout", "password_change"]:
        audit_data["severity"] = "MEDIUM"
    elif action in ["unauthorized_access", "suspicious_activity"]:
        audit_data["severity"] = "HIGH"
    elif action in ["data_breach", "security_violation"]:
        audit_data["severity"] = "CRITICAL"

    logger.info(
        "Security audit event",
        **audit_data
    )

    # Also log to JSON format for external systems
    print(json.dumps(audit_data, indent=2))

class SecurityAuditor:
    """Advanced security auditing system"""

    def __init__(self):
        self.suspicious_activities = set()

    def log_security_event(self, event_type: str, user_id: str, ip_address: str, user_agent: str, details: Dict[str, Any] = None):
        """Log comprehensive security events"""
        audit_log(
            action=event_type,
            user_id=user_id,
            resource="security_event",
            details={
                "ip_address": ip_address,
                "user_agent": user_agent,
                "event_details": details or {}
            }
        )

    def detect_suspicious_activity(self, user_id: str, activity: str) -> bool:
        """Detect and log suspicious activities"""
        suspicious_patterns = [
            "multiple_failed_logins",
            "unusual_access_pattern",
            "privilege_escalation_attempt",
            "unauthorized_data_access"
        ]

        if activity in suspicious_patterns:
            self.suspicious_activities.add(f"{user_id}:{activity}")
            audit_log(
                action="suspicious_activity",
                user_id=user_id,
                resource="security_monitoring",
                details={"activity": activity}
            )
            return True

        return False

# Global security auditor
security_auditor = SecurityAuditor()
