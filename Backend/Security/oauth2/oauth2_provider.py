"""
OAuth2 Provider Implementation
Supports multiple OAuth2 providers including Google, GitHub, and custom providers
"""
import asyncio
import json
import time
import secrets
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

from ...Redis.client import get_redis_client


class OAuth2Provider(Enum):
    """OAuth2 provider enumeration"""
    GOOGLE = "google"
    GITHUB = "github"
    CUSTOM = "custom"


@dataclass
class OAuth2Client:
    """OAuth2 client configuration"""
    client_id: str
    client_secret: str
    redirect_uri: str
    provider: OAuth2Provider
    scopes: List[str]
    name: str


@dataclass
class OAuth2Token:
    """OAuth2 token information"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_in: int
    scope: str
    created_at: float


class OAuth2ProviderService:
    """Advanced OAuth2 provider service with multi-provider support"""

    def __init__(self):
        self.redis_client = get_redis_client()
        self.oauth2_prefix = "oauth2_provider"

        # OAuth2 clients
        self.clients: Dict[str, OAuth2Client] = {}

        # Provider configurations
        self.provider_configs: Dict[OAuth2Provider, Dict[str, str]] = {
            OAuth2Provider.GOOGLE: {
                "auth_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo"
            },
            OAuth2Provider.GITHUB: {
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_info_url": "https://api.github.com/user"
            }
        }

        # OAuth2 statistics
        self.stats = {
            "auth_requests": 0,
            "successful_auths": 0,
            "failed_auths": 0,
            "token_refreshes": 0,
            "errors": 0
        }

    async def register_client(self, client: OAuth2Client) -> bool:
        """Register OAuth2 client"""
        try:
            # Store client configuration in Redis
            await self.redis_client.setex(
                f"{self.oauth2_prefix}:client:{client.client_id}",
                86400 * 30,  # 30 days
                json.dumps(asdict(client), default=str)
            )

            # Add to clients dictionary
            self.clients[client.client_id] = client

            return True

        except Exception as e:
            self.stats["errors"] += 1
            print(f"OAuth2 client registration error: {e}")
            return False

    async def generate_authorization_url(
        self,
        client_id: str,
        scope: str,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate OAuth2 authorization URL"""
        try:
            self.stats["auth_requests"] += 1

            # Get client
            client = self.clients.get(client_id)
            if not client:
                return {"error": "Invalid client ID"}

            # Generate state if not provided
            if not state:
                state = secrets.token_urlsafe(32)

            # Store state for validation
            await self.redis_client.setex(
                f"{self.oauth2_prefix}:state:{state}",
                600,  # 10 minutes
                client_id
            )

            # Get provider configuration
            provider_config = self.provider_configs.get(client.provider)
            if not provider_config:
                return {"error": "Unsupported provider"}

            # Build authorization URL
            auth_url = provider_config["auth_url"]
            params = {
                "client_id": client_id,
                "redirect_uri": client.redirect_uri,
                "scope": scope,
                "state": state,
                "response_type": "code"
            }

            # Format parameters
            param_string = "&".join([f"{key}={value}" for key, value in params.items()])
            full_auth_url = f"{auth_url}?{param_string}"

            return {
                "authorization_url": full_auth_url,
                "state": state,
                "provider": client.provider.value
            }

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Authorization URL generation error: {e}")
            return {"error": str(e)}

    async def exchange_code_for_token(
        self,
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str,
        state: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            # Validate state
            stored_client_id = await self.redis_client.get(f"{self.oauth2_prefix}:state:{state}")
            if not stored_client_id or stored_client_id != client_id:
                return {"error": "Invalid state parameter"}

            # Remove state
            await self.redis_client.delete(f"{self.oauth2_prefix}:state:{state}")

            # Get client
            client = self.clients.get(client_id)
            if not client:
                return {"error": "Invalid client ID"}

            # Validate client secret
            if client.client_secret != client_secret:
                return {"error": "Invalid client secret"}

            # Validate redirect URI
            if client.redirect_uri != redirect_uri:
                return {"error": "Invalid redirect URI"}

            # Get provider configuration
            provider_config = self.provider_configs.get(client.provider)
            if not provider_config:
                return {"error": "Unsupported provider"}

            # Exchange code for token (in production, would make HTTP request to provider)
            # For demo, we'll generate a mock token
            access_token = secrets.token_urlsafe(64)
            refresh_token = secrets.token_urlsafe(64)
            
            token = OAuth2Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="Bearer",
                expires_in=3600,  # 1 hour
                scope=client.scopes[0] if client.scopes else "",
                created_at=time.time()
            )

            # Store token
            await self.store_token(client_id, token)

            self.stats["successful_auths"] += 1

            return {
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "token_type": token.token_type,
                "expires_in": token.expires_in,
                "scope": token.scope
            }

        except Exception as e:
            self.stats["errors"] += 1
            self.stats["failed_auths"] += 1
            print(f"Token exchange error: {e}")
            return {"error": str(e)}

    async def refresh_token(self, client_id: str, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            # Get client
            client = self.clients.get(client_id)
            if not client:
                return {"error": "Invalid client ID"}

            # Get provider configuration
            provider_config = self.provider_configs.get(client.provider)
            if not provider_config:
                return {"error": "Unsupported provider"}

            # Validate refresh token (in production, would validate with provider)
            # For demo, we'll generate a new mock token
            new_access_token = secrets.token_urlsafe(64)
            
            new_token = OAuth2Token(
                access_token=new_access_token,
                refresh_token=refresh_token,  # Keep same refresh token
                token_type="Bearer",
                expires_in=3600,  # 1 hour
                scope=client.scopes[0] if client.scopes else "",
                created_at=time.time()
            )

            # Store new token
            await self.store_token(client_id, new_token)

            self.stats["token_refreshes"] += 1

            return {
                "access_token": new_token.access_token,
                "token_type": new_token.token_type,
                "expires_in": new_token.expires_in,
                "scope": new_token.scope
            }

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Token refresh error: {e}")
            return {"error": str(e)}

    async def store_token(self, client_id: str, token: OAuth2Token):
        """Store OAuth2 token"""
        try:
            # Store token with expiration
            await self.redis_client.setex(
                f"{self.oauth2_prefix}:token:{client_id}:{token.access_token}",
                token.expires_in,
                json.dumps(asdict(token), default=str)
            )

            # Store refresh token mapping
            if token.refresh_token:
                await self.redis_client.setex(
                    f"{self.oauth2_prefix}:refresh:{token.refresh_token}",
                    86400 * 30,  # 30 days
                    token.access_token
                )

        except Exception as e:
            print(f"Token storage error: {e}")

    async def validate_token(self, client_id: str, access_token: str) -> bool:
        """Validate access token"""
        try:
            # Get token from Redis
            token_data = await self.redis_client.get(f"{self.oauth2_prefix}:token:{client_id}:{access_token}")
            
            if not token_data:
                return False

            # Parse token
            token_info = OAuth2Token(**json.loads(token_data))
            
            # Check if token is expired
            if time.time() - token_info.created_at > token_info.expires_in:
                # Remove expired token
                await self.redis_client.delete(f"{self.oauth2_prefix}:token:{client_id}:{access_token}")
                return False

            return True

        except Exception as e:
            print(f"Token validation error: {e}")
            return False

    async def get_user_info(self, client_id: str, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth2 provider"""
        try:
            # Validate token first
            if not await self.validate_token(client_id, access_token):
                return {"error": "Invalid or expired token"}

            # Get client
            client = self.clients.get(client_id)
            if not client:
                return {"error": "Invalid client ID"}

            # Get provider configuration
            provider_config = self.provider_configs.get(client.provider)
            if not provider_config:
                return {"error": "Unsupported provider"}

            # Get user info (in production, would make HTTP request to provider)
            # For demo, return mock user info
            user_info = {
                "id": "oauth2_user_123",
                "email": "user@example.com",
                "name": "OAuth2 User",
                "provider": client.provider.value,
                "verified": True
            }

            return user_info

        except Exception as e:
            print(f"User info retrieval error: {e}")
            return {"error": str(e)}

    async def revoke_token(self, client_id: str, access_token: str) -> bool:
        """Revoke access token"""
        try:
            # Remove token from Redis
            await self.redis_client.delete(f"{self.oauth2_prefix}:token:{client_id}:{access_token}")
            
            return True

        except Exception as e:
            print(f"Token revocation error: {e}")
            return False

    async def get_oauth2_statistics(self) -> Dict[str, Any]:
        """Get OAuth2 provider statistics"""
        try:
            return {
                "oauth2_stats": self.stats.copy(),
                "registered_clients": len(self.clients),
                "timestamp": time.time()
            }

        except Exception as e:
            return {"error": str(e)}


# Global OAuth2 provider service instance
oauth2_provider = OAuth2ProviderService()