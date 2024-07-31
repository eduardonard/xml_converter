from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .constants import APP_CREDENTIALS

security = HTTPBasic()


def authenticate(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> None:
    valid = (
        credentials.username == APP_CREDENTIALS.username
        and credentials.password == APP_CREDENTIALS.password
    )
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
