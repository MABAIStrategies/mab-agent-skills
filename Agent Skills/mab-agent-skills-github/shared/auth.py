"""
MAB AI Strategies - Shared Authentication Module
Handles JWT validation, OAuth2 flows, and credential management
"""

import os
import jwt
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from google.cloud import kms
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi import HTTPException, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
KMS_KEY_PATH = f"projects/{os.getenv('GCP_PROJECT_ID')}/locations/{os.getenv('GCP_REGION')}/keyRings/{os.getenv('KMS_KEY_RING')}/cryptoKeys/{os.getenv('KMS_CRYPTO_KEY')}"

security = HTTPBearer()


class AuthError(Exception):
    """Custom authentication error"""
    pass


def encrypt_credential(plaintext: str) -> str:
    """
    Encrypt sensitive credentials using Google KMS
    
    Args:
        plaintext: Credential to encrypt
        
    Returns:
        Base64-encoded encrypted credential
    """
    try:
        kms_client = kms.KeyManagementServiceClient()
        encrypt_response = kms_client.encrypt(
            request={"name": KMS_KEY_PATH, "plaintext": plaintext.encode()}
        )
        return encrypt_response.ciphertext.decode('utf-8')
    except Exception as e:
        raise AuthError(f"Encryption failed: {str(e)}")


def decrypt_credential(ciphertext: str) -> str:
    """
    Decrypt credentials using Google KMS
    
    Args:
        ciphertext: Encrypted credential
        
    Returns:
        Decrypted plaintext credential
    """
    try:
        kms_client = kms.KeyManagementServiceClient()
        decrypt_response = kms_client.decrypt(
            request={"name": KMS_KEY_PATH, "ciphertext": ciphertext.encode()}
        )
        return decrypt_response.plaintext.decode('utf-8')
    except Exception as e:
        raise AuthError(f"Decryption failed: {str(e)}")


def create_jwt_token(user_id: str, email: str, roles: list = None) -> str:
    """
    Create a JWT token for authenticated users
    
    Args:
        user_id: Unique user identifier
        email: User email address
        roles: List of user roles
        
    Returns:
        Encoded JWT token
    """
    if roles is None:
        roles = ["user"]
    
    payload = {
        "user_id": user_id,
        "email": email,
        "roles": roles,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthError(f"Invalid token: {str(e)}")


def verify_webhook_signature(request_body: bytes, signature: str) -> bool:
    """
    Verify webhook request signature from Google Antigravity
    
    Args:
        request_body: Raw request body bytes
        signature: Signature from request header
        
    Returns:
        True if signature is valid
    """
    expected_signature = hashlib.sha256(
        WEBHOOK_SECRET.encode() + request_body
    ).hexdigest()
    
    return signature == expected_signature


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Header(None)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User information from decoded token
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    try:
        token = credentials.credentials
        user_data = verify_jwt_token(token)
        return user_data
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_roles(required_roles: list):
    """
    Decorator to enforce role-based access control
    
    Args:
        required_roles: List of required roles
        
    Returns:
        Decorated function with role check
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (injected by FastAPI dependency)
            user = kwargs.get('current_user')
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_roles = user.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires one of: {', '.join(required_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class OAuth2Manager:
    """Manage OAuth2 flows for external integrations"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, scopes: list, state: str = None) -> str:
        """
        Generate OAuth2 authorization URL
        
        Args:
            scopes: List of requested scopes
            state: State parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        # Implementation varies by provider (Gmail, LinkedIn, etc.)
        raise NotImplementedError("Override in provider-specific subclass")
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Token response with access_token and refresh_token
        """
        raise NotImplementedError("Override in provider-specific subclass")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token response
        """
        raise NotImplementedError("Override in provider-specific subclass")
    
    def store_credentials(self, user_id: str, credentials: Dict[str, Any]) -> None:
        """
        Securely store user credentials
        
        Args:
            user_id: User identifier
            credentials: OAuth credentials to store
        """
        from shared.database import get_firestore_client
        
        db = get_firestore_client()
        
        # Encrypt sensitive tokens
        encrypted_creds = {
            "access_token": encrypt_credential(credentials["access_token"]),
            "refresh_token": encrypt_credential(credentials.get("refresh_token", "")),
            "expires_at": credentials.get("expires_at"),
            "scope": credentials.get("scope"),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        db.collection("oauth_credentials").document(user_id).set(encrypted_creds)
    
    def get_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt stored credentials
        
        Args:
            user_id: User identifier
            
        Returns:
            Decrypted credentials or None if not found
        """
        from shared.database import get_firestore_client
        
        db = get_firestore_client()
        doc = db.collection("oauth_credentials").document(user_id).get()
        
        if not doc.exists:
            return None
        
        encrypted_creds = doc.to_dict()
        
        # Decrypt tokens
        return {
            "access_token": decrypt_credential(encrypted_creds["access_token"]),
            "refresh_token": decrypt_credential(encrypted_creds.get("refresh_token", "")),
            "expires_at": encrypted_creds.get("expires_at"),
            "scope": encrypted_creds.get("scope")
        }


# Rate limiting decorator
def rate_limit(max_calls: int, time_window: int):
    """
    Rate limiting decorator
    
    Args:
        max_calls: Maximum calls allowed
        time_window: Time window in seconds
    """
    def decorator(func):
        call_history = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_id = user['user_id']
            now = datetime.utcnow().timestamp()
            
            # Clean old entries
            if user_id in call_history:
                call_history[user_id] = [
                    t for t in call_history[user_id] 
                    if now - t < time_window
                ]
            else:
                call_history[user_id] = []
            
            # Check rate limit
            if len(call_history[user_id]) >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {max_calls} calls per {time_window}s"
                )
            
            # Record this call
            call_history[user_id].append(now)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
