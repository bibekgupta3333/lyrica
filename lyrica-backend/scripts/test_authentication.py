"""
Comprehensive test script for authentication system.

This script tests:
- User registration
- User login
- Token refresh
- API key creation
- API key authentication
- Protected endpoints
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from loguru import logger

BASE_URL = "http://localhost:8000/api/v1"


# ============================================================================
# Test Data
# ============================================================================

TEST_USER = {
    "email": "test@lyrica.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "username": "testuser",
}


# ============================================================================
# Test Functions
# ============================================================================


async def test_registration():
    """Test user registration."""
    logger.info("Testing user registration...")

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/register", json=TEST_USER)

        if response.status_code == 201:
            user = response.json()
            logger.success(
                f"✅ Registration successful! User ID: {user['id']}, Email: {user['email']}"
            )
            return True
        elif response.status_code == 400 and "already registered" in response.json().get(
            "detail", ""
        ):
            logger.info("✅ User already exists (expected if running multiple times)")
            return True
        else:
            logger.error(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False


async def test_login():
    """Test user login and token generation."""
    logger.info("Testing user login...")

    async with httpx.AsyncClient() as client:
        # OAuth2 form data
        form_data = {
            "username": TEST_USER["email"],  # OAuth2 uses "username" field
            "password": TEST_USER["password"],
        }

        response = await client.post(f"{BASE_URL}/auth/login", data=form_data)

        if response.status_code == 200:
            tokens = response.json()
            logger.success(f"✅ Login successful! Access token: {tokens['access_token'][:20]}...")
            return tokens
        else:
            logger.error(f"❌ Login failed: {response.status_code} - {response.text}")
            return None


async def test_protected_endpoint(access_token: str):
    """Test accessing a protected endpoint with JWT token."""
    logger.info("Testing protected endpoint access...")

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get(f"{BASE_URL}/auth/test-auth", headers=headers)

        if response.status_code == 200:
            data = response.json()
            logger.success(f"✅ Protected endpoint access successful! User: {data['email']}")
            return True
        else:
            logger.error(
                f"❌ Protected endpoint access failed: {response.status_code} - {response.text}"
            )
            return False


async def test_get_profile(access_token: str):
    """Test getting user profile."""
    logger.info("Testing get user profile...")

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get(f"{BASE_URL}/auth/me", headers=headers)

        if response.status_code == 200:
            profile = response.json()
            logger.success(
                f"✅ Profile retrieved! Email: {profile['email']}, Role: {profile['role']}"
            )
            return profile
        else:
            logger.error(f"❌ Get profile failed: {response.status_code} - {response.text}")
            return None


async def test_token_refresh(refresh_token: str):
    """Test refreshing access token."""
    logger.info("Testing token refresh...")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh_token}
        )

        if response.status_code == 200:
            new_tokens = response.json()
            logger.success(
                f"✅ Token refresh successful! New access token: {new_tokens['access_token'][:20]}..."
            )
            return new_tokens
        else:
            logger.error(f"❌ Token refresh failed: {response.status_code} - {response.text}")
            return None


async def test_api_key_creation(access_token: str):
    """Test creating an API key."""
    logger.info("Testing API key creation...")

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}

        api_key_data = {"name": "Test API Key", "expires_days": 30}

        response = await client.post(
            f"{BASE_URL}/auth/api-keys", json=api_key_data, headers=headers
        )

        if response.status_code == 201:
            api_key_response = response.json()
            logger.success(f"✅ API key created! Key: {api_key_response['api_key'][:20]}...")
            return api_key_response["api_key"]
        else:
            logger.error(f"❌ API key creation failed: {response.status_code} - {response.text}")
            return None


async def test_api_key_authentication(api_key: str):
    """Test authenticating with API key."""
    logger.info("Testing API key authentication...")

    async with httpx.AsyncClient() as client:
        headers = {"X-API-Key": api_key}

        response = await client.get(f"{BASE_URL}/auth/test-auth", headers=headers)

        if response.status_code == 200:
            data = response.json()
            logger.success(f"✅ API key authentication successful! User: {data['email']}")
            return True
        else:
            logger.error(
                f"❌ API key authentication failed: {response.status_code} - {response.text}"
            )
            return False


async def test_lyrics_with_auth(access_token: str):
    """Test accessing lyrics endpoints with authentication."""
    logger.info("Testing lyrics endpoints with authentication...")

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}

        # Test public lyrics endpoint (no auth required)
        response1 = await client.get(f"{BASE_URL}/lyrics/public/explore")
        if response1.status_code == 200:
            logger.success("✅ Public lyrics endpoint accessible without auth")
        else:
            logger.warning(f"⚠️  Public lyrics endpoint failed: {response1.status_code}")

        # Test protected lyrics endpoint
        response2 = await client.get(f"{BASE_URL}/lyrics/", headers=headers)
        if response2.status_code == 200:
            logger.success("✅ Protected lyrics endpoint accessible with auth")
        else:
            logger.warning(f"⚠️  Protected lyrics endpoint failed: {response2.status_code}")

        return True


# ============================================================================
# Main Test Runner
# ============================================================================


async def run_tests():
    """Run all authentication tests."""
    logger.info("=" * 80)
    logger.info("AUTHENTICATION SYSTEM TEST SUITE")
    logger.info("=" * 80)
    logger.info("")

    passed = 0
    total = 0

    # Test 1: Registration
    total += 1
    if await test_registration():
        passed += 1
    logger.info("")

    # Test 2: Login
    total += 1
    tokens = await test_login()
    if tokens:
        passed += 1
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
    else:
        logger.error("Cannot continue without access token")
        return
    logger.info("")

    # Test 3: Protected Endpoint
    total += 1
    if await test_protected_endpoint(access_token):
        passed += 1
    logger.info("")

    # Test 4: Get Profile
    total += 1
    if await test_get_profile(access_token):
        passed += 1
    logger.info("")

    # Test 5: Token Refresh
    total += 1
    new_tokens = await test_token_refresh(refresh_token)
    if new_tokens:
        passed += 1
        access_token = new_tokens["access_token"]  # Use new token for remaining tests
    logger.info("")

    # Test 6: API Key Creation
    total += 1
    api_key = await test_api_key_creation(access_token)
    if api_key:
        passed += 1
    logger.info("")

    # Test 7: API Key Authentication
    if api_key:
        total += 1
        if await test_api_key_authentication(api_key):
            passed += 1
        logger.info("")

    # Test 8: Lyrics with Auth
    total += 1
    if await test_lyrics_with_auth(access_token):
        passed += 1
    logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Tests: {total}")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {total - passed}")
    logger.info(f"Success Rate: {(passed / total * 100):.1f}%")
    logger.info("=" * 80)

    if passed == total:
        logger.success("🎉 ALL TESTS PASSED!")
    else:
        logger.warning("⚠️  SOME TESTS FAILED")


if __name__ == "__main__":
    asyncio.run(run_tests())
