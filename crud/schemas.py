from pydantic import BaseModel
from typing import Union


class User(BaseModel):
    name: str
    email_address: str
    password: str

    class Config:
        orm_mode = True

class ShowUser(BaseModel):
    name: str
    email_address: str

    class Config:
        orm_mode = True

class Login(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    access_token: str
    token_type: str

class Token(BaseModel):
    username: Union[str, None] = None