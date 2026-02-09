#!/usr/bin/env python3
"""
FastAPI Authentication Setup
Adds JWT-based authentication to a FastAPI project
"""

from pathlib import Path


def add_auth_to_project(output_dir: str = "app"):
    """Add JWT authentication to FastAPI project"""

    base_path = Path(output_dir)

    # Create auth directory
    auth_dir = base_path / "auth"
    auth_dir.mkdir(parents=True, exist_ok=True)
    (auth_dir / "__init__.py").touch()

    # Create auth utilities
    auth_utils = '''from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
'''

    (auth_dir / "utils.py").write_text(auth_utils, encoding='utf-8')
    print(f"[OK] Created auth/utils.py")

    # Create auth schemas
    auth_schemas = '''from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True
'''

    (base_path / "schemas" / "user.py").write_text(auth_schemas, encoding='utf-8')
    print(f"[OK] Created schemas/user.py")

    # Create auth dependencies
    auth_deps = '''from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.utils import decode_access_token, oauth2_scheme

# In-memory user storage (replace with database in production)
fake_users_db = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "is_active": True,
    }
}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Ensure user is active"""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
'''

    (auth_dir / "dependencies.py").write_text(auth_deps, encoding='utf-8')
    print(f"[OK] Created auth/dependencies.py")

    # Create auth endpoint
    auth_endpoint = '''from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.utils import verify_password, create_access_token
from app.auth.dependencies import get_current_active_user
from app.schemas.user import Token, User
from app.core.config import settings

router = APIRouter()

# In-memory user storage (replace with database)
fake_users_db = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "is_active": True,
    }
}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint - returns JWT token"""
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user
'''

    (base_path / "api" / "v1" / "endpoints" / "auth.py").write_text(auth_endpoint, encoding='utf-8')
    print(f"[OK] Created api/v1/endpoints/auth.py")

    # Update config to include auth settings
    config_addition = '''
# Authentication settings
SECRET_KEY: str = "your-secret-key-change-this-in-production"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
'''

    print(f"\n[NOTE] Add to app/core/config.py Settings class:")
    print(config_addition)

    print(f"\n[NOTE] Add to app/api/v1/api.py:")
    print("from app.api.v1.endpoints import auth")
    print('api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])')

    print(f"\n[NOTE] Add to requirements.txt:")
    print("python-jose[cryptography]>=3.3.0")
    print("passlib[bcrypt]>=1.7.4")
    print("python-multipart>=0.0.6")

    print(f"\n[INFO] Test credentials:")
    print("Username: testuser")
    print("Password: secret")

    print(f"\n[SUCCESS] Authentication setup completed!")
    print(f"\n[USAGE] Usage in protected endpoints:")
    print("from app.auth.dependencies import get_current_active_user")
    print("@router.get('/protected')")
    print("async def protected_route(user = Depends(get_current_active_user)):")
    print("    return {'message': f'Hello {user[\"username\"]}'}")


if __name__ == "__main__":
    add_auth_to_project()
