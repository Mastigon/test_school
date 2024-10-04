from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models.user import User

from app.schemas import InfoUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
SECRET_KEY = 'dadb93105700b35d2970ac8da856cd55af437ff48894bdaa84e7c09d79c9aa6be99aa630489ab33d217343ff9f7338d48460a2f632593e90d878b1c6371c1dad'
ALGORITHM = 'HS256'

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: str = payload.get('is_admin')
        is_user: str = payload.get('is_user')
        expire = payload.get('exp')
        if username is None or is_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        if datetime.now() > datetime.fromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired!"
            )
        return {
            'username': username,
            'id': user_id,
            'is_admin': is_admin,
            'is_user': is_user,
            }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user')


class GetUser:
    async def __call__(self, db: AsyncSession):
        pass
class CreateUser:
    async def __call__(self, user_info: InfoUser, db: AsyncSession):
        await db.execute(insert(User).values(first_name=user_info.first_name,
                                         last_name=user_info.last_name,
                                         username=user_info.username,
                                         email=user_info.email,
                                         hashed_password=bcrypt_context.hash(user_info.password),
                                         ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }

class LoginUser:

    @staticmethod
    async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
        user = await db.scalar(select(User).where(User.username == username))
        if not user or not bcrypt_context.verify(password, user.hashed_password) or user.is_active == False:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authentication credentials',
                                headers={'WWW-Authenticate': 'Bearer'})
        return user
    @staticmethod
    async def create_access_token(username: str, user_id: int, is_admin: bool, is_user: bool, expires_delta: timedelta):
        expires = datetime.now() + expires_delta
        encode = {'sub': username, 'id': user_id, 'is_admin': is_admin, 'is_user': is_user, 'exp': expires}
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


    async def __call__(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]):
        user = await self.authenticate_user(db, form_data.username, form_data.password)
        token = await self.create_access_token(user.username, user.id, user.is_admin, user.is_user, expires_delta=timedelta(minutes=20))
        return {
            'access_token': token,
            'token_type': 'bearer'
        }

# class CurrentUser:
#     async def __call__(self, user: dict = Depends(get_current_user)):
#         return {'User': user}

class UsersService:
    def __init__(self):
        self.get_user = GetUser()
        self.create_user = CreateUser()
        self.login_user = LoginUser()
        # self.current_user = CurrentUser()


