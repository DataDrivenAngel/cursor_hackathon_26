"""
Authentication dependencies and guards.
"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.connection import get_db
from app.database.schemas import TokenData
from app.auth.utils import decode_access_token
from app.models.database_models import User
import os


# HTTP Bearer token scheme
bearer_scheme = HTTPBearer()


# Check if we're in development mode (no auth)
def is_dev_mode() -> bool:
    """Check if running in development mode without auth."""
    return os.getenv("DISABLE_AUTH", "false").lower() == "true"


# Create a dummy user for development
class DummyUser:
    """Dummy user for development mode."""
    def __init__(self):
        self.id = 1
        self.username = "dev_user"
        self.email = "dev@example.com"
        self.role = "admin"
        self.is_active = True
        self.hashed_password = "dummy"
        self.created_at = None
        self.updated_at = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get the current authenticated user."""
    # Bypass authentication in dev mode
    if is_dev_mode():
        return DummyUser()
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Convert to int
    try:
        user_id = int(user_id)
    except ValueError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user


# Bypass admin check in dev mode
async def bypass_admin_check():
    """Dependency to bypass admin check in development mode."""
    if is_dev_mode():
        return DummyUser()
    # In production, require admin
    # This will be handled by the normal get_current_user + require_admin flow
    from app.auth.dependencies import get_current_user
    user = await get_current_user()
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    return current_user


def require_role(allowed_roles: List[str]):
    """Dependency factory to require specific roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not allowed. Required: {allowed_roles}"
            )
        return current_user
    return role_checker


# Pre-configured role dependencies
require_admin = require_role(["admin"])
require_organizer = require_role(["admin", "organizer"])
require_admin_or_organizer = require_role(["admin", "organizer"])
require_assistant = require_role(["admin", "organizer", "assistant"])
