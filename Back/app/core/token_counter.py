"""
Utilitaire pour compter les tokens des messages Mistral
"""
import tiktoken


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Compte le nombre de tokens dans un texte.
    Utilise le tokenizer de tiktoken (compatible avec Mistral).
    
    Args:
        text: Le texte à analyser
        model: Le modèle de tokenizer (par défaut gpt-3.5-turbo, compatible)
    
    Returns:
        Le nombre de tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        # Fallback simple: approximation basée sur les caractères
        # En moyenne, 1 token ≈ 4 caractères pour le français
        return len(text) // 4


def count_conversation_tokens(messages: list) -> int:
    """
    Compte le nombre de tokens dans une liste de messages.
    
    Args:
        messages: Liste de dictionnaires avec 'role' et 'content'
    
    Returns:
        Le nombre total de tokens
    """
    total = 0
    for msg in messages:
        # Compte le rôle
        total += count_tokens(msg.get('role', ''))
        # Compte le contenu
        total += count_tokens(msg.get('content', ''))
        # Overhead pour le formatage (environ 4 tokens par message)
        total += 4
    
    return total
