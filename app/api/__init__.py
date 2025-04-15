"""Centralized routers import"""

from .users.view import router as users_router
from .coworkings.view import router as coworkings_router
from .booking.view import router as booking_router
from .admins.view import router as admin_router
