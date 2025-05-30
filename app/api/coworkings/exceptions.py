from fastapi import HTTPException


class WrongFileTypeException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Wrong file type")
