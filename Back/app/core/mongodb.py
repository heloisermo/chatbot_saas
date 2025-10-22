"""
Configuration MongoDB avec Motor (async driver)
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("../.env")

# Configuration MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "chatbot_saas")

# Client MongoDB
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
users_collection = database.get_collection("users")
chatbots_collection = database.get_collection("chatbots")
conversations_collection = database.get_collection("conversations")


async def connect_to_mongo():
    """Connexion à MongoDB"""
    try:
        # Ping pour vérifier la connexion
        await client.admin.command('ping')
        print("✅ Connecté à MongoDB!")
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")


async def close_mongo_connection():
    """Fermeture de la connexion MongoDB"""
    client.close()
    print("🔌 Connexion MongoDB fermée")
