from enum import Enum


class SeatAccessLevel(str, Enum):
    """Guest/seat kyc level. Depends on profile fulfillment"""
    GUEST = "GUEST"
    STANDARD = "STANDARD"
    PRO = "PRO"


class VerificationLevel(str, Enum):
    """Guest/seat kyc level. Depends on profile fulfillment"""
    GUEST = "GUEST"
    STANDARD = "STANDARD"
    PRO = "PRO"


class RequiredLevel(str, Enum):
    AVAILABLE = "AVAILABLE"
    STANDARD = "STANDARD"
    PRO = "PRO"


class UserAccessLevel(str, Enum):
    GUEST = "GUEST"
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class TimeSlotType(str, Enum):
    INTERMEDIATE = "INTERMEDIATE"
    BOUNDARY = "BOUNDARY"


class SeatType(Enum):
    AUDIENCE = "AUDIENCE"
    OPENSPACE = "OPENSPACE"
