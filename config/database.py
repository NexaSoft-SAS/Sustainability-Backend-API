import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'sustainability_db')

if not mongo_url:
    raise ValueError("MONGO_URL environment variable is required")

client = AsyncIOMotorClient(mongo_url)
database = client[db_name]

def get_database():
    """Get database instance"""
    return database

async def connect_to_mongo():
    """Create database connection"""
    Database.client = client
    Database.database = database
    logger.info("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    if Database.client:
        Database.client.close()
        logger.info("Disconnected from MongoDB")

# Collections
def get_diagnostico_collection():
    return database.diagnosticos

def get_users_collection():
    return database.users