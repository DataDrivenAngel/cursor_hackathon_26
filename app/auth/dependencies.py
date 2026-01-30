"""
Authentication dependencies and guards.

In demo/development mode (DISABLE_AUTH=true), all endpoints run as a 
super admin user with full access. This is the default when running via run.sh.
"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.connection import get_db
from app.models.database_models import User
import os


# HTTP Bearer token scheme (only used when auth is enabled)
bearer_scheme = HTTPBearer(auto_error=False)


def is_dev_mode() -> bool:
    """Check if running in demo/development mode (no auth required).
    
    When DISABLE_AUTH=true (set by run.sh), all requests run as super admin.
    """
    return os.getenv("DISABLE_AUTH", "false").lower() == "true"


class SuperAdminUser:
    """Super admin user for demo/development mode.
    
    This user has full access to all features when running locally.
    """
    def __init__(self):
        self.id = 0
        self.username = "super_admin"
        self.email = "admin@demo.local"
        self.role = "admin"
        self.is_active = True
        self.hashed_password = ""
        self.created_at = None
        self.updated_at = None


# Singleton instance for dev mode
_super_admin = SuperAdminUser()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user.
    
    In demo mode (DISABLE_AUTH=true), returns super admin user.
    In production mode, validates JWT token and returns actual user.
    """
    # Demo mode - return super admin
    if is_dev_mode():
        return _super_admin
    
    # Production mode - require valid token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Import here to avoid circular dependency
    from app.auth.utils import decode_access_token
    
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    return current_user


def require_role(allowed_roles: List[str]):
    """Dependency factory to require specific roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # In dev mode, super admin has all permissions
        if is_dev_mode():
            return current_user
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

# Alias for backwards compatibility
bypass_admin_check = get_current_user
