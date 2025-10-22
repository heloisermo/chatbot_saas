"""
Script de démarrage du serveur backend
"""
import uvicorn
import os

# S'assurer qu'on est dans le bon répertoire
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Démarrage du serveur backend...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("⚠️  Utilisez CTRL+C pour arrêter\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
