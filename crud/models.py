from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class User(Base):
    __tablename__ = 'users'
    orm_mode = True
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email_address = Column(String)
    password = Column(String)
    last_login = Column(DateTime)