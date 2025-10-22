"""
Schémas Pydantic pour l'authentification
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schéma pour l'inscription"""
    prenom: str = Field(..., min_length=2, max_length=50)
    nom: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schéma pour la connexion"""
    email: EmailStr
    password: str


class UserInDB(BaseModel):
    """Schéma utilisateur en base de données"""
    id: str = Field(alias="_id")
    prenom: str
    nom: str
    email: EmailStr
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class UserUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur"""
    prenom: Optional[str] = Field(None, min_length=2, max_length=50)
    nom: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """Schéma pour la réponse utilisateur (sans mot de passe)"""
    id: str
    prenom: str
    nom: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    """Schéma pour le token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Données contenues dans le token"""
    email: Optional[str] = None
