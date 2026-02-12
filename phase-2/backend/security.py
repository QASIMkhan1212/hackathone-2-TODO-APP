import os
import logging
import httpx
import jwt
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    user_id: Optional[str] = None


# Use HTTPBearer for Better Auth tokens
security = HTTPBearer(auto_error=False)

# Better Auth frontend URL for fetching JWKS
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

# Cache for JWKS with TTL
_jwks_cache = None
_jwks_cache_time = 0
JWKS_CACHE_TTL = 3600  # 1 hour


async def get_jwks():
    """Fetch JWKS from Better Auth server with caching"""
    global _jwks_cache, _jwks_cache_time
    import time

    current_time = time.time()
    if _jwks_cache is not None and (current_time - _jwks_cache_time) < JWKS_CACHE_TTL:
        return _jwks_cache

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BETTER_AUTH_URL}/api/auth/jwks")
            if response.status_code == 200:
                _jwks_cache = response.json()
                _jwks_cache_time = current_time
                return _jwks_cache
    except Exception as e:
        logger.warning(f"Failed to fetch JWKS: {type(e).__name__}")
    return None


def get_public_key_from_jwks(jwks: dict, kid: Optional[str] = None):
    """Extract public key from JWKS"""
    if not jwks or "keys" not in jwks:
        return None

    keys = jwks["keys"]
    if not keys:
        return None

    # Find key by kid or use first key
    key_data = None
    for key in keys:
        if kid and key.get("kid") == kid:
            key_data = key
            break

    if key_data is None and keys:
        key_data = keys[0]

    if key_data is None:
        return None

    # For EdDSA (OKP) keys
    if key_data.get("kty") == "OKP" and key_data.get("crv") == "Ed25519":
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        import base64

        # Decode the x parameter (public key)
        x = key_data.get("x")
        if x:
            # Add padding if needed
            padding = 4 - len(x) % 4
            if padding != 4:
                x += "=" * padding
            public_key_bytes = base64.urlsafe_b64decode(x)
            return Ed25519PublicKey.from_public_bytes(public_key_bytes)

    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    token = credentials.credentials

    try:
        # First, decode without verification to get the header
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "EdDSA")
        kid = unverified_header.get("kid")

        if algorithm == "EdDSA":
            # Fetch JWKS and get public key
            jwks = await get_jwks()
            if jwks is None:
                raise credentials_exception

            public_key = get_public_key_from_jwks(jwks, kid)
            if public_key is None:
                raise credentials_exception

            # Verify token with public key
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["EdDSA"],
                options={"verify_aud": False}
            )
        else:
            # Fallback to HS256 with secret
            SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])

        # Better Auth stores user info in 'sub' claim
        user_id: str = payload.get("sub") or payload.get("user_id") or payload.get("userId")
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id)

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    except Exception:
        raise credentials_exception

    return token_data
