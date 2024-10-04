
from pydantic import EmailStr, BaseModel, constr, SecretStr, validator


class InfoProduct(BaseModel):
=======
from pydantic import BaseModel


class CreateProduct(BaseModel):

    name: str
    description: str
    price: int
    image_url: str
    stock: int


class InfoUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str

    @validator('first_name', 'last_name')
    def name_must_contain_at_least_one_character(cls, v):
        if not v:
            raise ValueError('Имя и фамилия должны содержать минимум 1 символ')
        return v

    @validator('password')
    def password_must_contain_at_least_four_characters(cls, v):
        if len(v) < 4:
            raise ValueError('Пароль должен содержать минимум 4 символа')
        return v
=======

