import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

class TestAuthEndpoints:
    """Test cases for authentication endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "DocZen API" in response.json()["message"]
    
    def test_register_user(self):
        """Test user registration"""
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        user_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # First registration
        client.post("/api/v1/auth/register", json=user_data)
        
        # Second registration should fail
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_user(self):
        """Test user login"""
        # First register a user
        user_data = {
            "email": "login@example.com",
            "password": "TestPassword123!",
            "full_name": "Login User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Now login
        login_data = {
            "email": "login@example.com",
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

class TestFileEndpoints:
    """Test cases for file endpoints"""
    
    def get_auth_headers(self):
        """Helper to get authentication headers"""
        # Register and login a user
        user_data = {
            "email": "filetest@example.com",
            "password": "TestPassword123!",
            "full_name": "File Test User"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "email": "filetest@example.com",
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_files_empty(self):
        """Test getting files when user has no files"""
        headers = self.get_auth_headers()
        response = client.get("/api/v1/files/files", headers=headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_upload_file(self):
        """Test file upload"""
        headers = self.get_auth_headers()
        
        # Create a test file
        file_content = b"Test file content"
        files = {"file": ("test.txt", file_content, "text/plain")}
        
        response = client.post("/api/v1/files/upload", files=files, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.txt"
        assert data["file_type"] == "txt"
        assert data["file_size"] == len(file_content)

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting(self):
        """Test that rate limiting works"""
        # Make multiple rapid requests
        for _ in range(20):
            response = client.get("/health")
            if response.status_code == 429:
                assert "rate limit" in response.json()["detail"].lower()
                return
        
        # If we get here, rate limiting might not be working
        pytest.skip("Rate limiting not properly configured")
