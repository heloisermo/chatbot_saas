"""
Configuration pour le système RAG
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class RAGConfig(BaseSettings):
    """Configuration pour le système RAG"""
    
    # Chemins
    upload_dir: str = "data/uploads"
    index_path: str = "data/faiss_index"
    
    # Modèle d'embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"  # "cpu" ou "cuda"
    
    # Paramètres de chunking
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200
    
    # Paramètres de recherche
    default_k_results: int = 4
    default_score_threshold: Optional[float] = None
    
    # Types de fichiers supportés
    allowed_extensions: list = [".pdf", ".txt", ".md"]
    max_file_size_mb: int = 10  # Taille maximale en MB
    
    class Config:
        env_prefix = "RAG_"
        case_sensitive = False


# Instance globale de configuration
config = RAGConfig()


# Créer les dossiers nécessaires
os.makedirs(config.upload_dir, exist_ok=True)
os.makedirs(os.path.dirname(config.index_path), exist_ok=True)
