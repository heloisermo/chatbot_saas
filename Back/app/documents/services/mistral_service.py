"""
Service Mistral AI
"""
from typing import List, Dict, Iterator
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate

from app.core.config import config


class MistralService:
    """Service pour interagir avec Mistral AI"""
    
    def __init__(self):
        """Initialise le service Mistral"""
        if not config.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY non configurée. Définissez MISTRAL_API_KEY dans le fichier .env")
        
        # Initialiser le modèle Mistral
        self.llm = ChatMistralAI(
            api_key=config.mistral_api_key,
            model=config.mistral_model,
            temperature=0.3
        )
        
        # Template de prompt
        self.prompt_template = PromptTemplate(
            template="""
{system_prompt}

Contexte:
{context}

Question: {question}

Réponse:""",
            input_variables=["system_prompt", "context", "question"]
        )
    
    def generate_response_stream(self, context: str, question: str, system_prompt: str = None, conversation_history: List[Dict] = None) -> Iterator[str]:
        """
        Génère une réponse en streaming basée sur le contexte et la question
        
        Args:
            context: Contexte extrait des documents
            question: Question de l'utilisateur
            system_prompt: Prompt système personnalisé (optionnel)
            conversation_history: Historique de conversation (optionnel) - Limité aux 3 derniers échanges
            
        Yields:
            Chunks de la réponse générée par le LLM
        """
        # Utiliser le prompt personnalisé ou celui par défaut
        prompt_to_use = system_prompt if system_prompt else config.system_prompt
        
        # Construire l'historique si présent (limité aux 2-3 derniers échanges)
        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            # Garder seulement les 4 derniers messages (2 échanges)
            recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
            
            history_parts = []
            for msg in recent_history:
                role = "Utilisateur" if msg.get("role") == "user" else "Assistant"
                content = msg.get("content", "")
                # Limiter la longueur de chaque message à 500 caractères pour ne pas surcharger
                if len(content) > 500:
                    content = content[:500] + "..."
                history_parts.append(f"{role}: {content}")
            
            if history_parts:
                history_text = "\n\nHistorique récent de la conversation:\n" + "\n".join(history_parts)
        
        # Générer le prompt avec ou sans historique
        if history_text:
            full_prompt = f"""{prompt_to_use}

Contexte des documents:
{context}
{history_text}

Question actuelle: {question}

Réponse:"""
        else:
            full_prompt = self.prompt_template.format(
                system_prompt=prompt_to_use,
                context=context,
                question=question
            )
        
        for chunk in self.llm.stream(full_prompt):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    def chat(self, messages: List[Dict[str, str]], context: str = "") -> str:
        """
        Conversation avec le modèle
        
        Args:
            messages: Liste de messages [{role: "user/assistant", content: "..."}]
            context: Contexte optionnel des documents
            
        Returns:
            Réponse générée
        """
        # Construire le prompt avec l'historique
        conversation = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}" 
            for msg in messages
        ])
        
        if context:
            full_prompt = f"{config.system_prompt}\n\nContexte:\n{context}\n\nConversation:\n{conversation}\n\nRéponse:"
        else:
            full_prompt = f"{config.system_prompt}\n\nConversation:\n{conversation}\n\nRéponse:"
        
        response = self.llm.invoke(full_prompt)
        return response.content