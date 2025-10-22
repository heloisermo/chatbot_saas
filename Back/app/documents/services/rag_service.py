"""
Service RAG - Retrieval Augmented Generation
"""
from typing import List, Dict, Iterator, Tuple, Optional

from app.documents.services.document_indexer import DocumentIndexer
from app.documents.services.mistral_service import MistralService


class RAGService:
    """Service pour les requêtes RAG (Retrieval + Generation)"""
    
    def __init__(self, chatbot_id: str = None):
        """
        Initialise le service RAG
        
        Args:
            chatbot_id: ID du chatbot pour un index spécifique
        """
        self.indexer = DocumentIndexer(chatbot_id=chatbot_id)
        self.mistral = MistralService()
    
    def index_exists(self) -> bool:
        """Vérifie si un index existe pour ce chatbot"""
        return self.indexer.vector_store is not None
    
    def query(self, question: str, k: int = 4, system_prompt: str = None) -> Dict:
        """
        Effectue une requête RAG
        
        Args:
            question: Question de l'utilisateur
            k: Nombre de documents à récupérer
            system_prompt: Prompt système personnalisé (optionnel)
            
        Returns:
            Dictionnaire avec la réponse et les sources
        """
        if self.indexer.vector_store is None:
            return {
                "answer": "Aucun document n'a été indexé. Veuillez d'abord uploader des documents.",
                "sources": []
            }
        
        # Récupérer les documents pertinents
        docs_with_scores = self.indexer.search(question, k=k)
        
        if not docs_with_scores:
            return {
                "answer": "Je n'ai pas trouvé d'informations pertinentes dans les documents indexés.",
                "sources": []
            }
        
        # Préparer le contexte
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}" 
            for i, (doc, _) in enumerate(docs_with_scores)
        ])
        
        # Obtenir la réponse du LLM via Mistral
        answer = self.mistral.generate_response(context, question, system_prompt=system_prompt)
        
        # Préparer les sources
        sources = []
        for i, (doc, score) in enumerate(docs_with_scores):
            sources.append({
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata,
                "score": float(score),
                "index": i + 1
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "question": question
        }
    
    def chat(self, messages: List[Dict[str, str]], k: int = 4) -> Dict:
        """
        Conversation multi-tour avec contexte RAG
        
        Args:
            messages: Liste de messages [{role: "user/assistant", content: "..."}]
            k: Nombre de documents à récupérer
            
        Returns:
            Dictionnaire avec la réponse et les sources
        """
        # Prendre la dernière question de l'utilisateur
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return {
                "answer": "Aucune question détectée.",
                "sources": []
            }
        
        last_question = user_messages[-1]["content"]
        
        # Utiliser la méthode query standard
        return self.query(last_question, k=k)
    
    def query_stream(self, question: str, k: int = 4, system_prompt: str = None, conversation_history: List[Dict] = None):
        """
        Effectue une requête RAG avec streaming de la réponse
        
        Args:
            question: Question de l'utilisateur
            k: Nombre de documents à récupérer
            system_prompt: Prompt système personnalisé (optionnel)
            conversation_history: Historique de conversation (optionnel) - Liste de {role, content}
            
        Returns:
            Tuple (Iterator de chunks de réponse, Liste des sources, Usage container)
            Le usage_container sera rempli après la fin du stream
        """
        sources = []
        
        if self.indexer.vector_store is None:
            def empty_stream():
                yield "Aucun document n'a été indexé. Veuillez d'abord uploader des documents."
            return empty_stream(), sources, {}
        
        # Récupérer les documents pertinents
        docs_with_scores = self.indexer.search(question, k=k)
        
        
        if not docs_with_scores:
            def no_docs_stream():
                yield "Je n'ai pas trouvé d'informations pertinentes dans les documents indexés."
            return no_docs_stream(), sources, {}
        
        # Préparer le contexte des documents
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}" 
            for i, (doc, _) in enumerate(docs_with_scores)
        ])
        
        # Préparer les sources
        for i, (doc, score) in enumerate(docs_with_scores):
            sources.append({
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata,
                "score": float(score),
                "index": i + 1
            })
        
        # Stream la réponse du LLM via Mistral avec l'historique
        response_stream, usage_container = self.mistral.generate_response_stream(
            context, 
            question, 
            system_prompt=system_prompt,
            conversation_history=conversation_history
        )
        
        return response_stream, sources, usage_container
