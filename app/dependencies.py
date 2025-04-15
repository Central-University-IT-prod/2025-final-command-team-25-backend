from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db, get_db_connection
from service import authorize

session = Annotated[AsyncSession, Depends(get_db)]
connection = Annotated[str, Depends(get_db_connection)]
Auth = Annotated[str, Depends(authorize)]
