from fastapi import HTTPException


class SeatAlreadyBookedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Booking for this seat already exists")

class NoSuchBookingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="No such booking")

class NoAccessException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="No access")

class CoworkingNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Coworking with this uuid not found")

class DateValidationException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid date")

class InvitationExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invitation expired or limit exceeded")
        