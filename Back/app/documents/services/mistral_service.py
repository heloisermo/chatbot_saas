"""
Service Mistral AI
"""
from typing import List, Dict
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
    
    def generate_response(self, context: str, question: str, system_prompt: str = None) -> str:
        """
        Génère une réponse basée sur le contexte et la question
        
        Args:
            context: Contexte extrait des documents
            question: Question de l'utilisateur
            system_prompt: Prompt système personnalisé (optionnel)
            
        Returns:
            Réponse générée par le LLM
        """
        # Utiliser le prompt personnalisé ou celui par défaut
        prompt_to_use = system_prompt if system_prompt else config.system_prompt
        
        # Générer le prompt
        prompt = self.prompt_template.format(
            system_prompt=prompt_to_use,
            context=context,
            question=question
        )
        
        # LOG: Afficher ce qui est envoyé à Mistral
        print("\n" + "="*80)
        print("🔍 PROMPT ENVOYÉ À MISTRAL:")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
        # Obtenir la réponse du LLM
        response = self.llm.invoke(prompt)
        
        # LOG: Afficher la réponse de Mistral
        print("\n" + "="*80)
        print("💬 RÉPONSE DE MISTRAL:")
        print("="*80)
        print(response.content)
        print("="*80 + "\n")
        
        return response.content
    
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
