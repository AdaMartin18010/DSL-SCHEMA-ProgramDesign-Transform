"""
API Integration Tests
=====================

API集成测试

Version: 2.2.0
"""

import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestHealthEndpoints:
    def test_health(self):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            assert response.status_code == 200
        except requests.ConnectionError:
            pytest.skip("API not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
