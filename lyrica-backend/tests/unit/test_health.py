"""
Unit tests for health check endpoints.
"""

import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
    
    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/api/v1/health/ready")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "timestamp" in data
    
    def test_liveness_check(self, client):
        """Test liveness check endpoint."""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data
    
    def test_system_metrics(self, client):
        """Test system metrics endpoint."""
        response = client.get("/api/v1/health/metrics")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
    
    def test_application_info(self, client):
        """Test application info endpoint."""
        response = client.get("/api/v1/health/info")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "application" in data
        assert "ollama" in data
        assert "features" in data
        assert data["application"]["name"] == "Lyrica"


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["application"] == "Lyrica"
        assert "version" in data
        assert data["status"] == "running"

