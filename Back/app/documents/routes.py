"""
Routes API pour la gestion des documents et du RAG
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Body
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
import os
import shutil
from pathlib import Path

from app.documents.services.document_indexer import DocumentIndexer
from app.documents.services.rag_service import RAGService
from app.core.config import config

router = APIRouter(prefix="/documents", tags=["documents"])

# Instance globale de l'indexeur
indexer = DocumentIndexer(
    index_path=config.index_path,
    embedding_model=config.embedding_model
)

# Instance globale du service RAG
try:
    rag_service = RAGService(indexer)
except ValueError as e:
    print(f"⚠️  Service RAG non initialisé: {e}")
    rag_service = None


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Form(config.default_chunk_size),
    chunk_overlap: int = Form(config.default_chunk_overlap),
    auto_index: bool = Form(True)
):
    """Upload un document et l'indexe automatiquement"""
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in config.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non supporté. Extensions autorisées: {config.allowed_extensions}"
        )
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    max_size = config.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux. Taille maximale: {config.max_file_size_mb}MB"
        )
    
    file_path = os.path.join(config.upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = {
            "filename": file.filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "status": "uploaded"
        }
        
        if auto_index:
            index_result = indexer.index_document(
                file_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                metadata={"filename": file.filename}
            )
            result["indexation"] = index_result
        
        return JSONResponse(content=result, status_code=201)
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")


@router.post("/index/{filename}")
async def index_document(
    filename: str,
    chunk_size: int = config.default_chunk_size,
    chunk_overlap: int = config.default_chunk_overlap
):
    """Indexe un document déjà uploadé"""
    file_path = os.path.join(config.upload_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    result = indexer.index_document(
        file_path,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        metadata={"filename": filename}
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.post("/search")
async def search_documents(
    query: str = Form(...),
    k: int = Form(config.default_k_results),
    score_threshold: Optional[float] = Form(config.default_score_threshold)
):
    """Recherche dans les documents indexés"""
    results = indexer.search(query, k=k, score_threshold=score_threshold)
    
    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)
        })
    
    return {
        "query": query,
        "results_count": len(formatted_results),
        "results": formatted_results
    }


@router.get("/stats")
async def get_index_stats():
    """Retourne les statistiques de l'index FAISS"""
    return indexer.get_index_stats()


@router.delete("/index")
async def delete_index():
    """Supprime l'index FAISS"""
    try:
        indexer.delete_index()
        return {"status": "success", "message": "Index supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.get("/files")
async def list_uploaded_files():
    """Liste tous les fichiers uploadés"""
    files = []
    for filename in os.listdir(config.upload_dir):
        file_path = os.path.join(config.upload_dir, filename)
        if os.path.isfile(file_path):
            files.append({
                "filename": filename,
                "size": os.path.getsize(file_path),
                "path": file_path
            })
    
    return {"files": files, "count": len(files)}


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Supprime un fichier uploadé"""
    file_path = os.path.join(config.upload_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    try:
        os.remove(file_path)
        return {"status": "success", "message": f"Fichier {filename} supprimé"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


@router.get("/config")
async def get_config():
    """Retourne la configuration actuelle du système RAG"""
    return {
        "embedding_model": config.embedding_model,
        "default_chunk_size": config.default_chunk_size,
        "default_chunk_overlap": config.default_chunk_overlap,
        "default_k_results": config.default_k_results,
        "allowed_extensions": config.allowed_extensions,
        "max_file_size_mb": config.max_file_size_mb,
        "llm_enabled": rag_service is not None,
        "mistral_model": config.mistral_model if rag_service else None
    }


@router.post("/query")
async def query_documents(
    question: str = Form(...),
    k: int = Form(config.default_k_results),
    system_prompt: Optional[str] = Form(None)
):
    """Pose une question sur les documents indexés avec RAG"""
    if not rag_service:
        raise HTTPException(
            status_code=503,
            detail="Service RAG non disponible. Vérifiez la configuration de MISTRAL_API_KEY."
        )
    
    try:
        result = rag_service.query(question, k=k, system_prompt=system_prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la requête: {str(e)}")


@router.post("/chat")
async def chat_with_documents(
    messages: List[Dict[str, str]] = Body(...),
    k: int = Body(config.default_k_results)
):
    """Conversation avec les documents indexés"""
    if not rag_service:
        raise HTTPException(
            status_code=503,
            detail="Service RAG non disponible. Vérifiez la configuration de MISTRAL_API_KEY."
        )
    
    try:
        result = rag_service.chat(messages, k=k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chat: {str(e)}")
