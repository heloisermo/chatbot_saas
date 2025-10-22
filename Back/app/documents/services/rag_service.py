"""
Service RAG - Retrieval Augmented Generation
"""
from typing import List, Dict

from app.documents.services.document_indexer import DocumentIndexer
from app.documents.services.mistral_service import MistralService


class RAGService:
    """Service pour les requêtes RAG (Retrieval + Generation)"""
    
    def __init__(self, indexer: DocumentIndexer):
        """
        Initialise le service RAG
        
        Args:
            indexer: Instance du DocumentIndexer
        """
        self.indexer = indexer
        self.mistral = MistralService()
    
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
        
        # LOG: Afficher ce qui a été trouvé
        print("\n" + "="*80)
        print(f"🔎 RECHERCHE DANS L'INDEX: '{question}'")
        print(f"📊 Nombre de documents trouvés: {len(docs_with_scores)}")
        print("="*80)
        for i, (doc, score) in enumerate(docs_with_scores):
            print(f"\nDocument {i+1} (score: {score:.4f}):")
            print(f"Contenu: {doc.page_content[:200]}...")
            print(f"Métadonnées: {doc.metadata}")
        print("="*80 + "\n")
        
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
