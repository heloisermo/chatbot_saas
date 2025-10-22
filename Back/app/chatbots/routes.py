"""
Routes pour la gestion des chatbots
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import json
import secrets

from app.chatbots.schemas import (
    ChatbotCreate, ChatbotUpdate, ChatbotResponse, 
    ChatbotQueryRequest, ChatbotQueryResponse,
    DocumentInfo, ConversationMessage
)
from app.auth.utils import get_current_user
from app.core.mongodb import chatbots_collection, conversations_collection
from app.documents.services.document_indexer import DocumentIndexer
from app.documents.services.rag_service import RAGService
from app.core.config import settings
import os

router = APIRouter(prefix="/chatbots", tags=["chatbots"])


@router.post("", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
async def create_chatbot(
    chatbot_data: ChatbotCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Créer un nouveau chatbot pour l'utilisateur connecté
    """
    # Générer un token unique pour le lien de partage
    share_token = secrets.token_urlsafe(32)
    
    new_chatbot = {
        "name": chatbot_data.name,
        "description": chatbot_data.description,
        "system_prompt": chatbot_data.system_prompt or settings.DEFAULT_SYSTEM_PROMPT,
        "user_id": str(current_user["_id"]),
        "share_token": share_token,
        "documents": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await chatbots_collection.insert_one(new_chatbot)
    created_chatbot = await chatbots_collection.find_one({"_id": result.inserted_id})
    
    # Générer les liens de partage
    base_url = settings.FRONTEND_URL or "http://localhost:5173"
    share_link = f"{base_url}/chat/{share_token}"
    widget_link = f"{base_url}/widget/{share_token}"
    
    # Générer le code d'intégration iframe
    embed_code = f'<iframe src="{widget_link}" width="100%" height="600" frameborder="0" style="border-radius: 10px;"></iframe>'
    
    return ChatbotResponse(
        id=str(created_chatbot["_id"]),
        name=created_chatbot["name"],
        description=created_chatbot.get("description"),
        system_prompt=created_chatbot.get("system_prompt"),
        user_id=created_chatbot["user_id"],
        share_link=share_link,
        widget_link=widget_link,
        embed_code=embed_code,
        documents=[],
        created_at=created_chatbot["created_at"],
        updated_at=created_chatbot["updated_at"]
    )


@router.get("", response_model=List[ChatbotResponse])
async def list_chatbots(current_user: dict = Depends(get_current_user)):
    """
    Lister tous les chatbots de l'utilisateur connecté
    """
    chatbots_cursor = chatbots_collection.find({"user_id": str(current_user["_id"])})
    chatbots = await chatbots_cursor.to_list(length=100)
    
    base_url = settings.FRONTEND_URL or "http://localhost:5173"
    
    result = []
    for chatbot in chatbots:
        documents = [
            DocumentInfo(
                filename=doc["filename"],
                upload_date=doc["upload_date"],
                chunks_count=doc.get("chunks_count")
            )
            for doc in chatbot.get("documents", [])
        ]
        
        # Générer les liens de partage
        share_link = None
        widget_link = None
        embed_code = None
        if chatbot.get("share_token"):
            share_link = f"{base_url}/chat/{chatbot['share_token']}"
            widget_link = f"{base_url}/widget/{chatbot['share_token']}"
            embed_code = f'<iframe src="{widget_link}" width="100%" height="600" frameborder="0" style="border-radius: 10px;"></iframe>'
        
        result.append(ChatbotResponse(
            id=str(chatbot["_id"]),
            name=chatbot["name"],
            description=chatbot.get("description"),
            system_prompt=chatbot.get("system_prompt"),
            user_id=chatbot["user_id"],
            share_link=share_link,
            widget_link=widget_link,
            embed_code=embed_code,
            documents=documents,
            created_at=chatbot["created_at"],
            updated_at=chatbot["updated_at"]
        ))
    
    return result


@router.get("/{chatbot_id}", response_model=ChatbotResponse)
async def get_chatbot(
    chatbot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer un chatbot spécifique
    """
    try:
        chatbot = await chatbots_collection.find_one({
            "_id": ObjectId(chatbot_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de chatbot invalide"
        )
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    documents = [
        DocumentInfo(
            filename=doc["filename"],
            upload_date=doc["upload_date"],
            chunks_count=doc.get("chunks_count")
        )
        for doc in chatbot.get("documents", [])
    ]
    
    # Générer les liens de partage
    base_url = settings.FRONTEND_URL or "http://localhost:5173"
    share_link = None
    widget_link = None
    embed_code = None
    if chatbot.get("share_token"):
        share_link = f"{base_url}/chat/{chatbot['share_token']}"
        widget_link = f"{base_url}/widget/{chatbot['share_token']}"
        embed_code = f'<iframe src="{widget_link}" width="100%" height="600" frameborder="0" style="border-radius: 10px;"></iframe>'
    
    return ChatbotResponse(
        id=str(chatbot["_id"]),
        name=chatbot["name"],
        description=chatbot.get("description"),
        system_prompt=chatbot.get("system_prompt"),
        user_id=chatbot["user_id"],
        share_link=share_link,
        widget_link=widget_link,
        embed_code=embed_code,
        documents=documents,
        created_at=chatbot["created_at"],
        updated_at=chatbot["updated_at"]
    )


@router.put("/{chatbot_id}", response_model=ChatbotResponse)
async def update_chatbot(
    chatbot_id: str,
    chatbot_data: ChatbotUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Mettre à jour un chatbot
    """
    try:
        chatbot = await chatbots_collection.find_one({
            "_id": ObjectId(chatbot_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de chatbot invalide"
        )
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    # Préparer les données à mettre à jour
    update_data = {"updated_at": datetime.utcnow()}
    if chatbot_data.name is not None:
        update_data["name"] = chatbot_data.name
    if chatbot_data.description is not None:
        update_data["description"] = chatbot_data.description
    if chatbot_data.system_prompt is not None:
        update_data["system_prompt"] = chatbot_data.system_prompt
    
    await chatbots_collection.update_one(
        {"_id": ObjectId(chatbot_id)},
        {"$set": update_data}
    )
    
    updated_chatbot = await chatbots_collection.find_one({"_id": ObjectId(chatbot_id)})
    
    documents = [
        DocumentInfo(
            filename=doc["filename"],
            upload_date=doc["upload_date"],
            chunks_count=doc.get("chunks_count")
        )
        for doc in updated_chatbot.get("documents", [])
    ]
    
    return ChatbotResponse(
        id=str(updated_chatbot["_id"]),
        name=updated_chatbot["name"],
        description=updated_chatbot.get("description"),
        system_prompt=updated_chatbot.get("system_prompt"),
        user_id=updated_chatbot["user_id"],
        documents=documents,
        created_at=updated_chatbot["created_at"],
        updated_at=updated_chatbot["updated_at"]
    )


@router.delete("/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chatbot(
    chatbot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprimer un chatbot
    """
    try:
        chatbot = await chatbots_collection.find_one({
            "_id": ObjectId(chatbot_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de chatbot invalide"
        )
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    # Supprimer le chatbot
    await chatbots_collection.delete_one({"_id": ObjectId(chatbot_id)})
    
    # Supprimer les conversations associées
    await conversations_collection.delete_many({"chatbot_id": chatbot_id})
    
    # Supprimer l'index FAISS associé si existe
    index_path = os.path.join(settings.FAISS_INDEX_PATH, f"{chatbot_id}.faiss")
    if os.path.exists(index_path):
        os.remove(index_path)


@router.post("/{chatbot_id}/documents", response_model=ChatbotResponse)
async def upload_document_to_chatbot(
    chatbot_id: str,
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    current_user: dict = Depends(get_current_user)
):
    """
    Uploader et indexer un document pour un chatbot spécifique
    """
    try:
        chatbot = await chatbots_collection.find_one({
            "_id": ObjectId(chatbot_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de chatbot invalide"
        )
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    # Créer le dossier pour ce chatbot
    chatbot_upload_dir = os.path.join(settings.UPLOAD_DIR, chatbot_id)
    os.makedirs(chatbot_upload_dir, exist_ok=True)
    
    # Sauvegarder le fichier
    file_path = os.path.join(chatbot_upload_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Indexer le document
    indexer = DocumentIndexer(chatbot_id)
    indexation_result = indexer.index_document(
        file_path,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Ajouter le document à la liste des documents du chatbot
    document_info = {
        "filename": file.filename,
        "upload_date": datetime.now(),
        "chunks_count": indexation_result["chunks_created"]
    }
    
    await chatbots_collection.update_one(
        {"_id": ObjectId(chatbot_id)},
        {
            "$push": {"documents": document_info},
            "$set": {"updated_at": datetime.now()}
        }
    )
    
    updated_chatbot = await chatbots_collection.find_one({"_id": ObjectId(chatbot_id)})
    
    documents = [
        DocumentInfo(
            filename=doc["filename"],
            upload_date=doc["upload_date"],
            chunks_count=doc.get("chunks_count")
        )
        for doc in updated_chatbot.get("documents", [])
    ]
    
    return ChatbotResponse(
        id=str(updated_chatbot["_id"]),
        name=updated_chatbot["name"],
        description=updated_chatbot.get("description"),
        system_prompt=updated_chatbot.get("system_prompt"),
        user_id=updated_chatbot["user_id"],
        documents=documents,
        created_at=updated_chatbot["created_at"],
        updated_at=updated_chatbot["updated_at"]
    )


@router.post("/{chatbot_id}/query", response_model=ChatbotQueryResponse)
async def query_chatbot(
    chatbot_id: str,
    query_data: ChatbotQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Poser une question à un chatbot spécifique
    """
    try:
        chatbot = await chatbots_collection.find_one({
            "_id": ObjectId(chatbot_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de chatbot invalide"
        )
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    # Utiliser le service RAG pour répondre
    rag_service = RAGService(chatbot_id)
    
    # Vérifier si l'index existe
    if not rag_service.index_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun document indexé pour ce chatbot"
        )
    
    result = rag_service.query(
        query_data.question,
        k=query_data.k,
        system_prompt=chatbot.get("system_prompt")
    )
    
    # Sauvegarder la conversation
    conversation_entry = {
        "chatbot_id": chatbot_id,
        "user_id": str(current_user["_id"]),
        "messages": [
            {
                "role": "user",
                "content": query_data.question,
                "timestamp": datetime.now()
            },
            {
                "role": "assistant",
                "content": result["answer"],
                "timestamp": datetime.now(),
                "sources": result["sources"]
            }
        ],
        "created_at": datetime.now()
    }
    
    await conversations_collection.insert_one(conversation_entry)
    
    return ChatbotQueryResponse(
        chatbot_id=chatbot_id,
        question=query_data.question,
        answer=result["answer"],
        sources=result["sources"],
        timestamp=datetime.now()
    )


@router.post("/{chatbot_id}/query/stream")
async def query_chatbot_stream(
    chatbot_id: str,
    query_data: ChatbotQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Poser une question à un chatbot spécifique avec réponse en streaming
    """
    try:
        chatbot = await chatbots_collection.find_one({
            "_id": ObjectId(chatbot_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de chatbot invalide"
        )
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    # Utiliser le service RAG pour répondre
    rag_service = RAGService(chatbot_id)
    
    # Vérifier si l'index existe
    if not rag_service.index_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun document indexé pour ce chatbot"
        )
    
    # Fonction générateur pour SSE
    async def event_generator():
        full_answer = ""
        
        # Obtenir le stream et les sources
        response_stream, sources = rag_service.query_stream(
            query_data.question,
            k=query_data.k,
            system_prompt=chatbot.get("system_prompt")
        )
        
        # Envoyer d'abord les sources
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
        
        # Stream la réponse
        try:
            for chunk in response_stream:
                if chunk:
                    full_answer += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        # Envoyer un message de fin
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        # Sauvegarder la conversation (en arrière-plan)
        try:
            conversation_entry = {
                "chatbot_id": chatbot_id,
                "user_id": str(current_user["_id"]),
                "messages": [
                    {
                        "role": "user",
                        "content": query_data.question,
                        "timestamp": datetime.now()
                    },
                    {
                        "role": "assistant",
                        "content": full_answer,
                        "timestamp": datetime.now(),
                        "sources": sources
                    }
                ],
                "created_at": datetime.now()
            }
            await conversations_collection.insert_one(conversation_entry)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la conversation: {e}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/{chatbot_id}/conversations", response_model=List[dict])
async def get_chatbot_conversations(
    chatbot_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer l'historique des conversations d'un chatbot
    """
    try:
        chatbot = await chatbots_collection.find_one({
            "_id": ObjectId(chatbot_id),
            "user_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de chatbot invalide"
        )
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    conversations_cursor = conversations_collection.find(
        {"chatbot_id": chatbot_id}
    ).sort("created_at", -1).limit(limit)
    
    conversations = await conversations_cursor.to_list(length=limit)
    
    # Convertir ObjectId en string
    for conv in conversations:
        conv["_id"] = str(conv["_id"])
    
    return conversations


@router.get("/public/{share_token}", response_model=ChatbotResponse)
async def get_public_chatbot(share_token: str):
    """
    Récupérer un chatbot via son token de partage (accès public)
    """
    chatbot = await chatbots_collection.find_one({"share_token": share_token})
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    documents = [
        DocumentInfo(
            filename=doc["filename"],
            upload_date=doc["upload_date"],
            chunks_count=doc.get("chunks_count")
        )
        for doc in chatbot.get("documents", [])
    ]
    
    # Générer le lien de partage
    base_url = settings.FRONTEND_URL or "http://localhost:5173"
    share_link = f"{base_url}/chat/{share_token}"
    
    return ChatbotResponse(
        id=str(chatbot["_id"]),
        name=chatbot["name"],
        description=chatbot.get("description"),
        system_prompt=chatbot.get("system_prompt"),
        user_id=chatbot["user_id"],
        share_link=share_link,
        documents=documents,
        created_at=chatbot["created_at"],
        updated_at=chatbot["updated_at"]
    )


@router.post("/public/{share_token}/query")
async def query_public_chatbot(
    share_token: str,
    query_request: ChatbotQueryRequest
):
    """
    Interroger un chatbot public via son token de partage (sans authentification)
    """
    chatbot = await chatbots_collection.find_one({"share_token": share_token})
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot non trouvé"
        )
    
    chatbot_id = str(chatbot["_id"])
    
    # Initialiser le service RAG
    rag_service = RAGService(chatbot_id=chatbot_id)
    
    # Vérifier si des documents sont indexés
    if not chatbot.get("documents") or len(chatbot["documents"]) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce chatbot n'a pas encore de documents indexés"
        )
    
    # Streaming de la réponse
    async def event_generator():
        try:
            answer_chunks = []
            
            # Obtenir le stream et les sources
            response_stream, sources = rag_service.query_stream(
                query_request.question,
                k=query_request.k,
                system_prompt=chatbot.get("system_prompt")
            )
            
            # Stream la réponse
            for chunk in response_stream:
                if chunk:
                    answer_chunks.append(chunk)
                    yield f"data: {json.dumps({'type': 'answer', 'content': chunk})}\n\n"
            
            # Envoyer les sources
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_message = f"Erreur: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
