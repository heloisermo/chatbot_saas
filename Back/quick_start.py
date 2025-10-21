"""
Guide de Démarrage Rapide - Système RAG
========================================

Ce guide vous montre comment utiliser le système d'indexation de documents
avec FAISS pour faire du RAG (Retrieval-Augmented Generation).
"""

# ========================================
# ÉTAPE 1: Installation
# ========================================

# Installer les dépendances
# pip install -r requirements.txt


# ========================================
# ÉTAPE 2: Lancer le serveur
# ========================================

# uvicorn app.main:app --reload


# ========================================
# ÉTAPE 3: Utilisation avec Python
# ========================================

import requests

BASE_URL = "http://localhost:8000"

# --- 1. Upload et indexation d'un document ---
def upload_and_index(file_path):
    """Upload et indexe un document"""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'auto_index': True
        }
        response = requests.post(f"{BASE_URL}/documents/upload", files=files, data=data)
        return response.json()

# Exemple
# result = upload_and_index("data/uploads/exemple_rag.txt")
# print(result)


# --- 2. Rechercher dans les documents ---
def search(query, k=4):
    """Recherche sémantique dans les documents"""
    data = {'query': query, 'k': k}
    response = requests.post(f"{BASE_URL}/documents/search", data=data)
    return response.json()

# Exemple
# results = search("Qu'est-ce que le RAG ?")
# for res in results['results']:
#     print(f"Score: {res['score']}")
#     print(f"Contenu: {res['content'][:200]}...")


# --- 3. Voir les statistiques ---
def get_stats():
    """Récupère les statistiques de l'index"""
    response = requests.get(f"{BASE_URL}/documents/stats")
    return response.json()

# Exemple
# stats = get_stats()
# print(f"Vecteurs indexés: {stats['total_vectors']}")


# ========================================
# ÉTAPE 4: Utilisation programmatique
# ========================================

from app.services.document_indexer import DocumentIndexer

# Créer l'indexeur
indexer = DocumentIndexer(
    index_path="data/faiss_index",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)

# Indexer un document
result = indexer.index_document(
    file_path="data/uploads/mon_document.pdf",
    chunk_size=1000,
    chunk_overlap=200,
    metadata={"author": "John Doe", "date": "2025-01-01"}
)

# Rechercher
results = indexer.search("ma requête", k=5)
for doc, score in results:
    print(f"Score: {score:.4f}")
    print(f"Contenu: {doc.page_content}")
    print(f"Métadonnées: {doc.metadata}")


# ========================================
# ÉTAPE 5: Test avec curl
# ========================================

# Upload d'un document
# curl -X POST "http://localhost:8000/documents/upload" \
#   -F "file=@document.pdf" \
#   -F "auto_index=true"

# Recherche
# curl -X POST "http://localhost:8000/documents/search" \
#   -F "query=Qu'est-ce que le RAG ?" \
#   -F "k=4"

# Statistiques
# curl -X GET "http://localhost:8000/documents/stats"


# ========================================
# CONFIGURATION (variables d'environnement)
# ========================================

# Créer un fichier .env à la racine du projet:
"""
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_DEFAULT_CHUNK_SIZE=1000
RAG_DEFAULT_CHUNK_OVERLAP=200
RAG_DEFAULT_K_RESULTS=4
RAG_MAX_FILE_SIZE_MB=10
"""


# ========================================
# TYPES DE FICHIERS SUPPORTÉS
# ========================================

# - PDF (.pdf)
# - Texte (.txt)
# - Markdown (.md)


# ========================================
# PROCHAINES ÉTAPES
# ========================================

# 1. Intégrer un modèle LLM (OpenAI, Anthropic, etc.)
# 2. Créer une chaîne RAG complète
# 3. Ajouter un système de conversation avec mémoire
# 4. Implémenter un re-ranking des résultats
# 5. Ajouter plus de formats (DOCX, HTML, etc.)


print("""
✅ Configuration terminée !

📚 Documentation complète: README_RAG.md
🧪 Tests disponibles: test_rag_complete.py, test_api_rag.py
🔧 Configuration: app/config.py
📁 Service d'indexation: app/services/document_indexer.py
🌐 Routes API: app/routes/documents.py

Pour démarrer:
1. uvicorn app.main:app --reload
2. Ouvrir http://localhost:8000/docs
3. Tester l'API avec les exemples ci-dessus

Bonne utilisation ! 🚀
""")
