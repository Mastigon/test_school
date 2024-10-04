from datetime import datetime
from typing import Annotated


from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from app.backend.db_depends import get_db

from app.schemas import InfoUser
from app.services.users_service import UsersService, get_current_user

router = APIRouter(prefix='/users', tags=['users'])

@router.post('/registration', status_code=status.HTTP_201_CREATED)
async def registration(user_info: InfoUser, db: Annotated[AsyncSession, Depends(get_db)], user_service: UsersService = Depends()):
    return await user_service.create_user(user_info, db)

@router.post('/login', status_code=status.HTTP_201_CREATED)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)], user_service: UsersService = Depends()):
    return await user_service.login_user(form_data, db)

@router.get('/read_current_user')
async def read_current_user(user: dict = Depends(get_current_user)):
    return {'User': user}
