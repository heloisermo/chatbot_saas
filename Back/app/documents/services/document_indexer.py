"""
Service d'indexation de documents pour RAG avec FAISS
"""
import os
import pickle
from typing import List, Optional
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


class DocumentIndexer:
    """Classe pour gérer l'indexation des documents avec FAISS"""
    
    def __init__(
        self, 
        chatbot_id: str = None,
        index_path: str = "data/faiss_index",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialise l'indexeur de documents
        
        Args:
            chatbot_id: ID du chatbot (pour des index séparés par chatbot)
            index_path: Chemin de base où sauvegarder l'index FAISS
            embedding_model: Modèle d'embeddings à utiliser
        """
        # Si un chatbot_id est fourni, créer un index spécifique
        if chatbot_id:
            self.index_path = os.path.join(index_path, chatbot_id)
        else:
            self.index_path = index_path
            
        self.embedding_model = embedding_model
        
        # Créer le dossier si nécessaire
        os.makedirs(self.index_path, exist_ok=True)
        
        # Initialiser les embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Charger l'index existant ou en créer un nouveau
        self.vector_store = self._load_or_create_index()
        
    def _load_or_create_index(self) -> Optional[FAISS]:
        """Charge l'index FAISS existant ou retourne None"""
        index_file = os.path.join(self.index_path, "index.faiss")
        if os.path.exists(index_file):
            try:
                return FAISS.load_local(
                    self.index_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Erreur lors du chargement de l'index: {e}")
                return None
        return None
    
    def load_document(self, file_path: str) -> List:
        """
        Charge un document depuis un fichier
        
        Args:
            file_path: Chemin du fichier à charger
            
        Returns:
            Liste de documents LangChain
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_extension in ['.txt', '.md']:
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"Type de fichier non supporté: {file_extension}")
        
        return loader.load()
    
    def split_documents(
        self, 
        documents: List,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List:
        """
        Divise les documents en chunks
        
        Args:
            documents: Liste de documents à diviser
            chunk_size: Taille de chaque chunk
            chunk_overlap: Chevauchement entre chunks
            
        Returns:
            Liste de chunks de documents
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        return text_splitter.split_documents(documents)
    
    def index_document(
        self,
        file_path: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Indexe un document dans FAISS
        
        Args:
            file_path: Chemin du document à indexer
            chunk_size: Taille des chunks
            chunk_overlap: Chevauchement entre chunks
            metadata: Métadonnées additionnelles à ajouter
            
        Returns:
            Dictionnaire avec les statistiques d'indexation
        """
        try:
            # Charger le document
            documents = self.load_document(file_path)
            
            # Ajouter les métadonnées personnalisées
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Diviser en chunks
            chunks = self.split_documents(documents, chunk_size, chunk_overlap)
            
            # Créer ou mettre à jour l'index FAISS
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            else:
                # Ajouter les nouveaux documents à l'index existant
                new_vector_store = FAISS.from_documents(chunks, self.embeddings)
                self.vector_store.merge_from(new_vector_store)
            
            # Sauvegarder l'index
            self.save_index()
            
            return {
                "status": "success",
                "file": file_path,
                "chunks_created": len(chunks),
                "total_documents": len(documents)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "file": file_path,
                "error": str(e)
            }
    
    def index_multiple_documents(
        self,
        file_paths: List[str],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[dict]:
        """
        Indexe plusieurs documents
        
        Args:
            file_paths: Liste des chemins de fichiers
            chunk_size: Taille des chunks
            chunk_overlap: Chevauchement entre chunks
            
        Returns:
            Liste des résultats d'indexation
        """
        results = []
        for file_path in file_paths:
            result = self.index_document(file_path, chunk_size, chunk_overlap)
            results.append(result)
        
        return results
    
    def search(
        self,
        query: str,
        k: int = 4,
        score_threshold: Optional[float] = None
    ) -> List[tuple]:
        """
        Recherche dans l'index FAISS
        
        Args:
            query: Requête de recherche
            k: Nombre de résultats à retourner
            score_threshold: Seuil de score minimum (optionnel)
            
        Returns:
            Liste de tuples (document, score)
        """
        if self.vector_store is None:
            return []
        
        if score_threshold is not None:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            # Filtrer par seuil de score
            results = [(doc, score) for doc, score in results if score >= score_threshold]
        else:
            results = self.vector_store.similarity_search_with_score(query, k=k)
        
        return results
    
    def save_index(self):
        """Sauvegarde l'index FAISS sur le disque"""
        if self.vector_store is not None:
            self.vector_store.save_local(self.index_path)
    
    def delete_index(self):
        """Supprime l'index FAISS"""
        if os.path.exists(self.index_path):
            import shutil
            shutil.rmtree(self.index_path)
        self.vector_store = None
    
    def get_index_stats(self) -> dict:
        """
        Retourne les statistiques de l'index
        
        Returns:
            Dictionnaire avec les statistiques
        """
        if self.vector_store is None:
            return {
                "indexed": False,
                "total_vectors": 0
            }
        
        return {
            "indexed": True,
            "total_vectors": self.vector_store.index.ntotal,
            "embedding_dimension": self.vector_store.index.d,
            "index_path": self.index_path
        }
