"""
Authentication dependencies - simplified for local development.

All authentication has been disabled for local development.
"""
from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
import os


class DevUser:
    """Dev user for local development (no authentication)."""
    def __init__(self):
        self.id = 1
        self.username = "dev_user"
        self.email = "dev@local.local"
        self.role = "admin"
        self.is_active = True


# Singleton dev user
_dev_user = DevUser()


async def get_current_user(
    db: AsyncSession = Depends(get_db)
):
    """Get the current user - always returns dev user in local mode."""
    return _dev_user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """Ensure the current user is active - always passes in local mode."""
    return current_user


def require_role(allowed_roles: list):
    """Dependency factory to require specific roles - always passes in local mode."""
    async def role_checker(current_user = Depends(get_current_user)) -> dict:
        return current_user
    return role_checker


# Pre-configured role dependencies (always pass in local mode)
require_admin = require_role(["admin"])
require_organizer = require_role(["admin", "organizer"])
require_admin_or_organizer = require_role(["admin", "organizer"])
require_assistant = require_role(["admin", "organizer", "assistant"])

# Alias for backwards compatibility
bypass_admin_check = get_current_user
