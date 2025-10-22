"""
Calcul des coûts Mistral AI
"""

# Tarifs Mistral Small Latest (par million de tokens)
MISTRAL_SMALL_INPUT_COST = 0.1  # $0.1 par million de tokens input
MISTRAL_SMALL_OUTPUT_COST = 0.3  # $0.3 par million de tokens output


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calcule le coût estimé basé sur les tokens utilisés
    
    Args:
        prompt_tokens: Nombre de tokens du prompt (input)
        completion_tokens: Nombre de tokens de la réponse (output)
    
    Returns:
        Coût en dollars
    """
    # Calculer le coût pour chaque type de token
    input_cost = (prompt_tokens / 1_000_000) * MISTRAL_SMALL_INPUT_COST
    output_cost = (completion_tokens / 1_000_000) * MISTRAL_SMALL_OUTPUT_COST
    
    return input_cost + output_cost


def format_cost(cost: float) -> str:
    """
    Formate le coût pour l'affichage
    
    Args:
        cost: Coût en dollars
    
    Returns:
        Chaîne formatée (ex: "$0.0012")
    """
    return f"${cost:.6f}"
