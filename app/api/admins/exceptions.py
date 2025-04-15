from fastapi import HTTPException


class NoAdminAccessException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="No admin access")


class NoSuchBookingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No such booking")

class WrongQRException(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail="Wrong QR data")

class BookingNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail="Wrong QR data")


class NoSuchUserException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No such user")