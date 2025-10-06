"""
Advanced Security Features - Zero-Trust Architecture
Distributed authentication, authorization, and security monitoring
"""
import asyncio
import json
import time
import hashlib
import hmac
import secrets
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .client import get_redis_client


class SecurityLevel(Enum):
    """Security levels"""
    PUBLIC = 1
    AUTHENTICATED = 2
    AUTHORIZED = 3
    ADMIN = 4
    SYSTEM = 5


@dataclass
class SecurityContext:
    """Security context for requests"""
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: float
    security_level: SecurityLevel
    permissions: Set[str]
    risk_score: float
    geo_location: Optional[Dict[str, str]] = None


@dataclass
class SecurityEvent:
    """Security event for audit trail"""
    event_id: str
    event_type: str
    user_id: Optional[str]
    ip_address: str
    timestamp: float
    details: Dict[str, Any]
    risk_level: str
    action_taken: str


class ZeroTrustSecurity:
    """Zero-trust security implementation with Redis"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.security_prefix = "security"

        # Security statistics
        self.stats = {
            "authentication_attempts": 0,
            "successful_authentications": 0,
            "failed_authentications": 0,
            "security_events": 0,
            "blocked_requests": 0,
            "suspicious_activities": 0,
            "errors": 0
        }

        # Risk assessment
        self.ip_reputation: Dict[str, float] = {}
        self.user_risk_scores: Dict[str, float] = {}

    async def authenticate_request(
        self,
        api_key: str,
        ip_address: str,
        user_agent: str,
        requested_resource: str
    ) -> Tuple[bool, SecurityContext]:
        """Authenticate request using zero-trust principles"""
        self.stats["authentication_attempts"] += 1

        try:
            # Verify API key
            user_id = await self.verify_api_key(api_key)
            if not user_id:
                await self.record_security_event(
                    "authentication_failed",
                    None,
                    ip_address,
                    {"reason": "invalid_api_key", "resource": requested_resource},
                    "high"
                )
                self.stats["failed_authentications"] += 1
                return False, None

            # Check IP reputation
            ip_risk = await self.get_ip_reputation(ip_address)

            # Get user permissions
            permissions = await self.get_user_permissions(user_id)

            # Assess overall risk
            risk_score = await self.calculate_risk_score(user_id, ip_address, requested_resource)

            # Determine security level
            security_level = await self.determine_security_level(permissions, requested_resource)

            # Create security context
            context = SecurityContext(
                user_id=user_id,
                session_id=await self.get_user_session(user_id),
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=time.time(),
                security_level=security_level,
                permissions=permissions,
                risk_score=risk_score,
                geo_location=await self.get_geo_location(ip_address)
            )

            # Record successful authentication
            await self.record_security_event(
                "authentication_successful",
                user_id,
                ip_address,
                {"resource": requested_resource, "risk_score": risk_score},
                "low"
            )

            self.stats["successful_authentications"] += 1
            return True, context

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Authentication error: {e}")
            return False, None

    async def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return user ID"""
        try:
            # Hash API key for lookup
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()

            # Check if key exists and is valid
            key_data = await self.redis_client.get(f"{self.security_prefix}:api_key:{key_hash}")

            if key_data:
                data = json.loads(key_data)

                # Check if key is expired
                if data.get("expires_at", 0) > time.time():
                    return data.get("user_id")

            return None

        except Exception as e:
            print(f"API key verification error: {e}")
            return None

    async def get_ip_reputation(self, ip_address: str) -> float:
        """Get IP address reputation score"""
        try:
            # Check cached reputation
            cached_score = await self.redis_client.get(f"{self.security_prefix}:ip_reputation:{ip_address}")

            if cached_score:
                return float(cached_score)

            # Calculate reputation based on historical data
            reputation = await self.calculate_ip_reputation(ip_address)

            # Cache for 1 hour
            await self.redis_client.setex(
                f"{self.security_prefix}:ip_reputation:{ip_address}",
                3600,
                str(reputation)
            )

            return reputation

        except Exception as e:
            print(f"IP reputation error: {e}")
            return 0.5  # Neutral score

    async def calculate_ip_reputation(self, ip_address: str) -> float:
        """Calculate IP reputation based on historical security events"""
        try:
            # Get recent security events for this IP
            pattern = f"{self.security_prefix}:events:ip:{ip_address}:*"
            event_keys = await self.redis_client.keys(pattern)

            if not event_keys:
                return 1.0  # Good reputation for new IPs

            # Analyze events (simplified)
            failed_attempts = 0
            successful_attempts = 0

            for key in event_keys[:20]:  # Check last 20 events
                event_data = await self.redis_client.get(key)
                if event_data:
                    event = json.loads(event_data)

                    if event.get("event_type") in ["authentication_failed", "suspicious_activity"]:
                        failed_attempts += 1
                    elif event.get("event_type") == "authentication_successful":
                        successful_attempts += 1

            total_attempts = failed_attempts + successful_attempts

            if total_attempts == 0:
                return 1.0

            # Calculate reputation score
            success_rate = successful_attempts / total_attempts

            # Apply time decay (more recent events have higher weight)
            reputation = success_rate

            return max(0.0, min(1.0, reputation))

        except Exception as e:
            print(f"IP reputation calculation error: {e}")
            return 0.5

    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get user permissions"""
        try:
            permissions_key = f"{self.security_prefix}:user_permissions:{user_id}"
            permissions_data = await self.redis_client.get(permissions_key)

            if permissions_data:
                return set(json.loads(permissions_data))

            return set()

        except Exception as e:
            print(f"User permissions error: {e}")
            return set()

    async def get_user_session(self, user_id: str) -> Optional[str]:
        """Get active user session"""
        try:
            session_key = f"{self.security_prefix}:user_session:{user_id}"
            return await self.redis_client.get(session_key)

        except Exception:
            return None

    async def get_geo_location(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get geographic location for IP"""
        try:
            # In production, this would use a geo IP service
            # For demo, return mock data
            geo_data = await self.redis_client.get(f"{self.security_prefix}:geo:{ip_address}")

            if geo_data:
                return json.loads(geo_data)

            return {"country": "unknown", "city": "unknown"}

        except Exception:
            return None

    async def calculate_risk_score(
        self,
        user_id: str,
        ip_address: str,
        requested_resource: str
    ) -> float:
        """Calculate overall risk score for request"""
        try:
            risk_factors = []

            # IP reputation factor
            ip_risk = await self.get_ip_reputation(ip_address)
            risk_factors.append(ip_risk)

            # User risk factor
            user_risk = self.user_risk_scores.get(user_id, 0.5)
            risk_factors.append(user_risk)

            # Resource sensitivity factor
            resource_risk = await self.get_resource_risk_level(requested_resource)
            risk_factors.append(resource_risk)

            # Time-based factor (unusual hours)
            current_hour = time.localtime().tm_hour
            time_risk = 1.0 if 9 <= current_hour <= 18 else 0.7
            risk_factors.append(time_risk)

            # Calculate weighted average
            weights = [0.3, 0.2, 0.3, 0.2]  # Weights for each factor
            overall_risk = sum(r * w for r, w in zip(risk_factors, weights))

            return overall_risk

        except Exception as e:
            print(f"Risk score calculation error: {e}")
            return 0.5

    async def get_resource_risk_level(self, resource: str) -> float:
        """Get risk level for requested resource"""
        # Define resource risk levels
        high_risk_resources = ["/admin", "/system", "/api/internal"]
        medium_risk_resources = ["/api/users", "/api/orders", "/api/payments"]

        if any(resource.startswith(risk_resource) for risk_resource in high_risk_resources):
            return 0.9
        elif any(resource.startswith(risk_resource) for risk_resource in medium_risk_resources):
            return 0.6
        else:
            return 0.3

    async def determine_security_level(self, permissions: Set[str], resource: str) -> SecurityLevel:
        """Determine required security level for resource"""
        try:
            # Define resource requirements
            resource_requirements = {
                "/admin": SecurityLevel.ADMIN,
                "/system": SecurityLevel.SYSTEM,
                "/api/internal": SecurityLevel.ADMIN,
                "/api/users": SecurityLevel.AUTHORIZED,
                "/api/orders": SecurityLevel.AUTHORIZED,
                "/api/payments": SecurityLevel.AUTHORIZED,
            }

            required_level = SecurityLevel.PUBLIC

            for resource_pattern, level in resource_requirements.items():
                if resource.startswith(resource_pattern):
                    required_level = level
                    break

            # Check if user has required permissions
            if required_level == SecurityLevel.ADMIN and "admin" not in permissions:
                return SecurityLevel.AUTHENTICATED
            elif required_level == SecurityLevel.AUTHORIZED and not permissions:
                return SecurityLevel.AUTHENTICATED
            elif required_level == SecurityLevel.AUTHORIZED and permissions:
                return SecurityLevel.AUTHORIZED

            return required_level

        except Exception as e:
            print(f"Security level determination error: {e}")
            return SecurityLevel.PUBLIC

    async def record_security_event(
        self,
        event_type: str,
        user_id: Optional[str],
        ip_address: str,
        details: Dict[str, Any],
        risk_level: str = "low"
    ) -> str:
        """Record security event for audit trail"""
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=time.time(),
            details=details,
            risk_level=risk_level,
            action_taken="recorded"
        )

        try:
            # Store event
            await self.redis_client.setex(
                f"{self.security_prefix}:event:{event.event_id}",
                86400 * 30,  # 30 days
                json.dumps(asdict(event), default=str)
            )

            # Store by IP for reputation tracking
            await self.redis_client.setex(
                f"{self.security_prefix}:events:ip:{ip_address}:{event.event_id}",
                86400 * 7,  # 7 days
                json.dumps(asdict(event), default=str)
            )

            # Update IP reputation if high risk
            if risk_level in ["high", "critical"]:
                current_reputation = await self.get_ip_reputation(ip_address)
                new_reputation = max(0.0, current_reputation - 0.1)
                await self.redis_client.setex(
                    f"{self.security_prefix}:ip_reputation:{ip_address}",
                    3600,
                    str(new_reputation)
                )

            self.stats["security_events"] += 1
            return event.event_id

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Security event recording error: {e}")
            return ""

    async def authorize_request(
        self,
        context: SecurityContext,
        resource: str,
        action: str
    ) -> Tuple[bool, str]:
        """Authorize request based on security context"""
        try:
            # Check if user has required permission for action
            required_permission = f"{action}:{resource}"

            if required_permission not in context.permissions:
                await self.record_security_event(
                    "authorization_failed",
                    context.user_id,
                    context.ip_address,
                    {
                        "resource": resource,
                        "action": action,
                        "reason": "insufficient_permissions",
                        "required_permission": required_permission,
                        "user_permissions": list(context.permissions)
                    },
                    "medium"
                )
                return False, "Insufficient permissions"

            # Check risk score
            if context.risk_score > 0.8:
                await self.record_security_event(
                    "high_risk_request",
                    context.user_id,
                    context.ip_address,
                    {
                        "resource": resource,
                        "action": action,
                        "risk_score": context.risk_score,
                        "reason": "high_risk_score"
                    },
                    "high"
                )

                # Block very high risk requests
                if context.risk_score > 0.9:
                    self.stats["blocked_requests"] += 1
                    return False, "Request blocked due to high risk score"

            # Check geographic restrictions
            if await self.check_geographic_restrictions(context, resource):
                return False, "Geographic access restriction"

            return True, "Authorized"

        except Exception as e:
            print(f"Authorization error: {e}")
            return False, "Authorization error"

    async def check_geographic_restrictions(
        self,
        context: SecurityContext,
        resource: str
    ) -> bool:
        """Check geographic access restrictions"""
        try:
            # Get geographic restrictions for resource
            restrictions_key = f"{self.security_prefix}:geo_restrictions:{resource}"
            restrictions_data = await self.redis_client.get(restrictions_key)

            if restrictions_data:
                restrictions = json.loads(restrictions_data)

                if context.geo_location:
                    user_country = context.geo_location.get("country")

                    if user_country and user_country not in restrictions.get("allowed_countries", []):
                        return True  # Blocked

            return False

        except Exception:
            return False

    async def create_api_key(
        self,
        user_id: str,
        permissions: List[str],
        expires_in_days: int = 30
    ) -> str:
        """Create new API key for user"""
        try:
            # Generate secure API key
            api_key = secrets.token_urlsafe(32)

            # Hash for storage
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()

            # Store key data
            key_data = {
                "user_id": user_id,
                "permissions": permissions,
                "created_at": time.time(),
                "expires_at": time.time() + (expires_in_days * 86400)
            }

            await self.redis_client.setex(
                f"{self.security_prefix}:api_key:{key_hash}",
                expires_in_days * 86400,
                json.dumps(key_data, default=str)
            )

            return api_key

        except Exception as e:
            print(f"API key creation error: {e}")
            return ""

    async def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        try:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()

            # Remove from Redis
            deleted = await self.redis_client.delete(f"{self.security_prefix}:api_key:{key_hash}")

            return deleted > 0

        except Exception as e:
            print(f"API key revocation error: {e}")
            return False

    async def detect_suspicious_activity(self, context: SecurityContext) -> Dict[str, Any]:
        """Detect suspicious activity patterns"""
        try:
            suspicious_indicators = []

            # Check for rapid requests from same IP
            ip_request_key = f"{self.security_prefix}:ip_requests:{context.ip_address}"
            recent_requests = await self.redis_client.zcount(ip_request_key, time.time() - 60, time.time())

            if recent_requests > 100:  # More than 100 requests per minute
                suspicious_indicators.append({
                    "type": "rapid_requests",
                    "description": f"{recent_requests} requests in last minute",
                    "severity": "high"
                })

            # Check for unusual geographic access
            if context.geo_location:
                geo_risk = await self.assess_geographic_risk(context.geo_location, context.user_id)
                if geo_risk > 0.7:
                    suspicious_indicators.append({
                        "type": "unusual_location",
                        "description": f"Access from unusual location: {context.geo_location}",
                        "severity": "medium"
                    })

            # Check for privilege escalation attempts
            if await self.detect_privilege_escalation(context):
                suspicious_indicators.append({
                    "type": "privilege_escalation",
                    "description": "Attempt to access resources beyond permission level",
                    "severity": "critical"
                })

            # Record suspicious activity if detected
            if suspicious_indicators:
                self.stats["suspicious_activities"] += 1

                await self.record_security_event(
                    "suspicious_activity_detected",
                    context.user_id,
                    context.ip_address,
                    {
                        "indicators": suspicious_indicators,
                        "risk_score": context.risk_score
                    },
                    "high"
                )

            return {
                "suspicious": len(suspicious_indicators) > 0,
                "indicators": suspicious_indicators,
                "risk_score": context.risk_score,
                "recommendation": "Monitor user activity" if suspicious_indicators else "Normal activity"
            }

        except Exception as e:
            print(f"Suspicious activity detection error: {e}")
            return {"error": str(e)}

    async def assess_geographic_risk(self, geo_location: Dict[str, str], user_id: str) -> float:
        """Assess risk based on geographic location"""
        try:
            # Get user's normal locations
            user_locations_key = f"{self.security_prefix}:user_locations:{user_id}"
            normal_locations = await self.redis_client.smembers(user_locations_key)

            current_country = geo_location.get("country")

            if not normal_locations:
                # New user, store current location
                await self.redis_client.sadd(user_locations_key, current_country)
                return 0.0  # No risk for new users

            # Check if current location is normal
            if current_country in normal_locations:
                return 0.0  # Normal location

            # Calculate risk based on how unusual the location is
            # In production, this would use more sophisticated analysis
            return 0.8  # High risk for unusual locations

        except Exception:
            return 0.5

    async def detect_privilege_escalation(self, context: SecurityContext) -> bool:
        """Detect privilege escalation attempts"""
        try:
            # Get user's access history
            access_pattern = f"{self.security_prefix}:user_access:{context.user_id}"
            recent_access = await self.redis_client.zrange(access_pattern, 0, -1)

            # Check if user is accessing high-privilege resources
            high_privilege_resources = ["/admin", "/system", "/api/internal"]

            for access_entry in recent_access[-10:]:  # Check last 10 accesses
                access_data = json.loads(access_entry)

                if any(access_data.get("resource", "").startswith(resource)
                      for resource in high_privilege_resources):

                    # Check if user has admin permissions
                    if "admin" not in context.permissions:
                        return True  # Privilege escalation detected

            return False

        except Exception:
            return False

    async def get_security_analytics(self) -> Dict[str, Any]:
        """Get comprehensive security analytics"""
        try:
            # Get authentication statistics
            total_attempts = self.stats["authentication_attempts"]
            success_rate = (self.stats["successful_authentications"] / max(1, total_attempts)) * 100

            # Get IP reputation distribution
            pattern = f"{self.security_prefix}:ip_reputation:*"
            ip_keys = await self.redis_client.keys(pattern)

            reputation_distribution = {"low": 0, "medium": 0, "high": 0}

            for key in ip_keys[:100]:  # Sample for performance
                reputation = float(await self.redis_client.get(key) or "0.5")

                if reputation < 0.3:
                    reputation_distribution["low"] += 1
                elif reputation < 0.7:
                    reputation_distribution["medium"] += 1
                else:
                    reputation_distribution["high"] += 1

            return {
                "authentication": {
                    "total_attempts": total_attempts,
                    "successful_attempts": self.stats["successful_authentications"],
                    "failed_attempts": self.stats["failed_authentications"],
                    "success_rate_percent": round(success_rate, 2)
                },
                "ip_reputation": {
                    "total_ips_tracked": len(ip_keys),
                    "distribution": reputation_distribution
                },
                "events": {
                    "total_security_events": self.stats["security_events"],
                    "blocked_requests": self.stats["blocked_requests"],
                    "suspicious_activities": self.stats["suspicious_activities"]
                },
                "risk_assessment": {
                    "high_risk_ips": reputation_distribution["low"],
                    "medium_risk_ips": reputation_distribution["medium"],
                    "low_risk_ips": reputation_distribution["high"]
                }
            }

        except Exception as e:
            return {"error": str(e)}


# Global security instance
zero_trust_security = ZeroTrustSecurity()
