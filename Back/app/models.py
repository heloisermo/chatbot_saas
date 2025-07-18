from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable= False)
    lastname = Column(String, nullable= False)
    company = Column(String, nullable= False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    verification_code = Column(String)
    code_expires_at = Column(TIMESTAMP)