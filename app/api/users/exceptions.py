from fastapi import HTTPException


class UserNameUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=409, detail={"place": "username"}
        )


class UserEmailUniqueException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail={"place": "email"})


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid credentials")


class NoSuchBookingException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No such booking")


class NoSuchUserException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No such user")


class NoAccessException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="No access")