"""
Routes d'authentification avec MongoDB
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime

from app.auth.schemas import UserRegister, UserLogin, Token, UserResponse, UserUpdate
from app.auth.utils import get_password_hash, verify_password, create_access_token, get_current_user
from app.core.mongodb import users_collection

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Inscription d'un nouvel utilisateur
    """
    # Vérifier si l'email existe déjà
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )
    
    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(user_data.password)
    
    new_user = {
        "prenom": user_data.prenom,
        "nom": user_data.nom,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(new_user)
    
    # Récupérer l'utilisateur créé
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    
    return UserResponse(
        id=str(created_user["_id"]),
        prenom=created_user["prenom"],
        nom=created_user["nom"],
        email=created_user["email"],
        created_at=created_user["created_at"]
    )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Connexion d'un utilisateur
    """
    # Trouver l'utilisateur par email
    user = await users_collection.find_one({"email": user_credentials.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier le mot de passe
    if not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token JWT
    access_token = create_access_token(data={"sub": user["email"]})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur connecté
    """
    return UserResponse(
        id=str(current_user["_id"]),
        prenom=current_user["prenom"],
        nom=current_user["nom"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Met à jour les informations de l'utilisateur connecté
    """
    update_data = {"updated_at": datetime.utcnow()}
    
    if user_data.prenom:
        update_data["prenom"] = user_data.prenom
    if user_data.nom:
        update_data["nom"] = user_data.nom
    if user_data.email:
        # Vérifier si l'email n'est pas déjà utilisé par un autre utilisateur
        existing_user = await users_collection.find_one({
            "email": user_data.email,
            "_id": {"$ne": current_user["_id"]}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
        update_data["email"] = user_data.email
    
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    updated_user = await users_collection.find_one({"_id": current_user["_id"]})
    
    return UserResponse(
        id=str(updated_user["_id"]),
        prenom=updated_user["prenom"],
        nom=updated_user["nom"],
        email=updated_user["email"],
        created_at=updated_user["created_at"]
    )
