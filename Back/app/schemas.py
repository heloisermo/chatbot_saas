from pydantic import BaseModel, EmailStr
from datetime import datetime

# Ce schéma sert pour l'inscription
class UserCreate(BaseModel):
    name: str
    lastname: str
    company: str
    email: EmailStr
    password: str 

# Ce schéma est utilisé pour afficher les infos d'un utilisateur (en réponse API)
class UserOut(BaseModel):
    id: int
    name: str
    lastname: str
    company: str
    email: EmailStr
    is_verified: bool
    code_expires_at: datetime

    class Config:
        orm_mode = True
