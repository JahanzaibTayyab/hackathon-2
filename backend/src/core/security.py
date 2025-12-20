"""JWT token verification and security utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any
import base64

from jose import JWTError, jwt as jose_jwt
import jwt as pyjwt
import httpx

from src.core.config import settings


async def get_jwks() -> dict[str, Any]:
    """
    Fetch JWKS from Better Auth endpoint.
    
    Returns:
        JWKS dictionary
    """
    jwks_url = f"{settings.better_auth_url}/api/auth/jwks"
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        return response.json()


async def verify_jwt_token_async(token: str) -> dict[str, Any] | None:
    """
    Verify JWT token using JWKS (for EdDSA tokens from Better Auth).
    
    Uses PyJWT which has better EdDSA support than python-jose.
    
    Args:
        token: JWT token string
        
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        
        # Get JWKS
        jwks = await get_jwks()
        
        # Decode token header to get key ID
        unverified_header = pyjwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            return None
        
        # Find the key in JWKS
        jwk_data = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                jwk_data = key
                break
        
        if not jwk_data:
            return None
        
        # Handle Ed25519 (EdDSA) keys
        if jwk_data.get("kty") == "OKP" and jwk_data.get("crv") == "Ed25519":
            x = jwk_data.get("x")
            if not x:
                return None
            
            # Decode base64url encoded public key
            # Add padding if needed
            padding = len(x) % 4
            if padding:
                x += "=" * (4 - padding)
            public_key_bytes = base64.urlsafe_b64decode(x)
            
            # Create Ed25519 public key
            public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            # Verify token with EdDSA using PyJWT
            # Disable audience validation since Better Auth tokens may not include 'aud' claim
            payload = pyjwt.decode(
                token,
                public_key,
                algorithms=["EdDSA"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": False,  # Better Auth tokens may not have audience
                },
            )
            return payload
        else:
            # For other key types, fall back to jose
            from jose import jwk
            key = jwk.construct(jwk_data)
            payload = jose_jwt.decode(
                token,
                key,
                algorithms=["RS256", "HS256"],
                options={"verify_signature": True},
            )
            return payload
    except Exception as e:
        # Log error for debugging
        print(f"JWT verification error: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_jwt_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create JWT token with payload.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.jwt_expiration_days)
    
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(
        to_encode,
        settings.better_auth_secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


async def extract_user_id_from_token_async(token: str) -> str | None:
    """
    Extract user_id from JWT token (async version for JWKS verification).
    
    Better Auth JWT tokens contain user_id in the 'sub' (subject) field.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID if valid, None otherwise
    """
    payload = await verify_jwt_token_async(token)
    if payload:
        # Better Auth stores user_id in 'sub' field (JWT standard)
        # Also check 'user_id' as fallback
        user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
        if user_id:
            return str(user_id)
    return None


def extract_user_id_from_token(token: str) -> str | None:
    """
    Extract user_id from JWT token (sync version, deprecated).
    
    Use extract_user_id_from_token_async instead.
    """
    # This is kept for backwards compatibility but should use async version
    return None
