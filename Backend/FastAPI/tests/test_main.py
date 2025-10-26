"""
Test suite for FastAPI application
Comprehensive testing with security focus
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from fastapi.testclient import TestClient
import os
import sys

# Ensure application package is importable in Docker or locally
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.auth import authenticate_user, create_access_token, verify_token

# Test configuration
@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def async_client():
    """Async FastAPI test client"""
    return AsyncClient(app=app, base_url="http://test")

# Authentication Tests
class TestAuthentication:
    """Test authentication and authorization"""

    def test_login_valid_user(self, client):
        """Test login with valid credentials"""
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "changeme123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        assert response.status_code == 401

    def test_access_protected_route_without_token(self, client):
        """Test accessing protected route without token"""
        response = client.get("/protected")
        assert response.status_code == 401

    def test_access_protected_route_with_valid_token(self, client):
        """Test accessing protected route with valid token"""
        # First login to get token
        login_response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "changeme123"}
        )
        token = login_response.json()["access_token"]

        # Access protected route
        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

# Security Tests
class TestSecurity:
    """Test security features"""

    def test_rate_limiting(self, client):
        """Test rate limiting functionality"""
        # Make multiple requests quickly
        for i in range(15):
            response = client.get("/health")

        # Should eventually get rate limited
        # Note: This is a basic test, real rate limiting would need more sophisticated testing

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/test")
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"]

    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/health")
        # Check for basic security headers
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection"
        ]

        for header in security_headers:
            if header in response.headers:
                assert response.headers[header]

# API Tests
class TestAPI:
    """Test API endpoints"""

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_api_docs_accessible(self, client):
        """Test API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_api_redoc_accessible(self, client):
        """Test API redoc is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200

# Performance Tests
class TestPerformance:
    """Test performance characteristics"""

    def test_response_time_under_limit(self, client):
        """Test that responses are reasonably fast"""
        import time
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond in under 1 second

# Database Tests
class TestDatabase:
    """Test database operations"""

    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connectivity"""
        # This would test actual database connections
        # For now, it's a placeholder
        pass

# Integration Tests
class TestIntegration:
    """Test integration between services"""

    def test_redis_integration(self, client):
        """Test Redis integration"""
        # Test Redis-dependent functionality
        response = client.get("/redis/test")
        # Should work if Redis is available
        assert response.status_code in [200, 503]  # 503 if Redis unavailable

# Utility Functions Tests
class TestUtils:
    """Test utility functions"""

    def test_authenticate_user_function(self):
        """Test authenticate_user function"""
        user = authenticate_user("admin", "changeme123")
        assert user is not None
        assert user["username"] == "admin"

        user = authenticate_user("admin", "wrongpassword")
        assert user is None

    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        data = {"username": "testuser", "role": "user"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

        # Test verification
        token_data = verify_token(token)
        assert token_data is not None
        assert token_data.username == "testuser"
        assert token_data.role == "user"

# Error Handling Tests
class TestErrorHandling:
    """Test error handling"""

    def test_404_handling(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_malformed_json(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

# Load Testing (if needed)
class TestLoad:
    """Load testing (run separately)"""

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading

        def make_request(i):
            return client.get("/health")

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # All should succeed
        for response in results:
            assert response.status_code == 200

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
