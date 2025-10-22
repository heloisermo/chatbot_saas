from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import routes as auth_routes
from app.documents import routes as documents_routes
from app.chatbots import routes as chatbots_routes
from app.core.mongodb import connect_to_mongo, close_mongo_connection

app = FastAPI(title="RAG Chatbot API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Événement au démarrage de l'application"""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Événement à l'arrêt de l'application"""
    await close_mongo_connection()


app.include_router(auth_routes.router)
app.include_router(documents_routes.router)
app.include_router(chatbots_routes.router)


@app.get("/")
async def root():
    return {"message": "RAG Chatbot API", "status": "running"}
