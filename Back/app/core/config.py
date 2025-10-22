"""
Configuration pour le système RAG
"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel

# Charger le .env manuellement
load_dotenv("../.env")


class RAGConfig(BaseModel):
    """Configuration pour le système RAG"""
    
    # Chemins
    upload_dir: str = "data/uploads"
    index_path: str = "data/faiss_index"
    
    # Modèle d'embeddings
    embedding_model: str = os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embedding_device: str = os.getenv("RAG_EMBEDDING_DEVICE", "cpu")  # "cpu" ou "cuda"
    
    # Paramètres de chunking
    default_chunk_size: int = int(os.getenv("RAG_DEFAULT_CHUNK_SIZE", "1000"))
    default_chunk_overlap: int = int(os.getenv("RAG_DEFAULT_CHUNK_OVERLAP", "200"))
    
    # Paramètres de recherche
    default_k_results: int = int(os.getenv("RAG_DEFAULT_K_RESULTS", "4"))
    default_score_threshold: Optional[float] = None
    
    # Types de fichiers supportés
    allowed_extensions: list = [".pdf", ".txt", ".md"]
    max_file_size_mb: int = int(os.getenv("RAG_MAX_FILE_SIZE_MB", "10"))  # Taille maximale en MB
    
    # LLM Configuration
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
    mistral_model: str = os.getenv("RAG_MISTRAL_MODEL", "mistral-small-latest")
    system_prompt: str = os.getenv("RAG_SYSTEM_PROMPT", """Tu es un assistant IA spécialisé dans la réponse aux questions basées sur des documents.
Utilise uniquement les informations fournies dans le contexte pour répondre aux questions.
Si l'information n'est pas dans le contexte, dis-le clairement.
Sois précis, concis et professionnel.""")


# Alias pour compatibilité
class Settings:
    """Wrapper pour accéder facilement à la config"""
    def __init__(self):
        self._config = RAGConfig()
    
    @property
    def UPLOAD_DIR(self):
        return self._config.upload_dir
    
    @property
    def FAISS_INDEX_PATH(self):
        return self._config.index_path
    
    @property
    def DEFAULT_SYSTEM_PROMPT(self):
        return self._config.system_prompt
    
    @property
    def MISTRAL_API_KEY(self):
        return self._config.mistral_api_key
    
    @property
    def MISTRAL_MODEL(self):
        return self._config.mistral_model
    
    @property
    def EMBEDDING_MODEL(self):
        return self._config.embedding_model
    
    @property
    def EMBEDDING_DEVICE(self):
        return self._config.embedding_device


# Instance globale de configuration
config = RAGConfig()
settings = Settings()


# Créer les dossiers nécessaires
os.makedirs(config.upload_dir, exist_ok=True)
os.makedirs(os.path.dirname(config.index_path), exist_ok=True)
