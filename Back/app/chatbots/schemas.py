"""
Schémas Pydantic pour les chatbots
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatbotCreate(BaseModel):
    """Schéma pour créer un chatbot"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    system_prompt: Optional[str] = Field(None, max_length=2000)


class ChatbotUpdate(BaseModel):
    """Schéma pour mettre à jour un chatbot"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    system_prompt: Optional[str] = Field(None, max_length=2000)


class DocumentInfo(BaseModel):
    """Information sur un document indexé"""
    filename: str
    upload_date: datetime
    chunks_count: Optional[int] = None


class ConversationMessage(BaseModel):
    """Message dans une conversation"""
    role: str  # 'user' ou 'assistant'
    content: str
    timestamp: datetime
    sources: Optional[List[dict]] = None


class ChatbotResponse(BaseModel):
    """Schéma de réponse pour un chatbot"""
    id: str
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_id: str
    documents: List[DocumentInfo] = []
    share_link: Optional[str] = None
    widget_link: Optional[str] = None
    embed_code: Optional[str] = None
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0  # Coût estimé en dollars
    created_at: datetime
    updated_at: datetime


class ChatbotQueryRequest(BaseModel):
    """Requête pour interroger un chatbot"""
    question: str = Field(..., min_length=1)
    k: int = Field(default=4, ge=1, le=10)
    conversation_history: Optional[List[dict]] = Field(default=None, max_length=10)


class ChatbotQueryResponse(BaseModel):
    """Réponse d'un chatbot"""
    chatbot_id: str
    question: str
    answer: str
    sources: List[dict] = []
    timestamp: datetime
