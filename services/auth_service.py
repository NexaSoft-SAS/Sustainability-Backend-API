from typing import Optional
from datetime import datetime, timedelta
import logging

from config.database import get_users_collection
from config.auth import verify_password, get_password_hash, create_access_token
from models.user import UserLogin, UserCreate, UserResponse, UserInDB, TokenResponse

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.collection = get_users_collection()
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[TokenResponse]:
        """Authenticate user and return token"""
        try:
            # Find user by email
            user_doc = await self.collection.find_one({"email": login_data.email})
            
            if not user_doc:
                logger.warning(f"Login attempt with non-existent email: {login_data.email}")
                return None
            
            user = UserInDB(
                _id=str(user_doc["_id"]),
                email=user_doc["email"],
                password_hash=user_doc["password_hash"],
                role=user_doc["role"],
                created_at=user_doc["created_at"]
            )
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                logger.warning(f"Invalid password for user: {login_data.email}")
                return None
            
            # Create access token
            access_token = create_access_token(
                data={"sub": user.email, "role": user.role}
            )
            
            user_response = UserResponse.from_mongo({
                "_id": user.id,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at
            })
            
            logger.info(f"User authenticated successfully: {login_data.email}")
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=24 * 3600,  # 24 hours in seconds
                user=user_response
            )
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    async def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await self.collection.find_one({"email": user_data.email})
            
            if existing_user:
                logger.warning(f"Attempt to create existing user: {user_data.email}")
                return None
            
            # Hash password
            password_hash = get_password_hash(user_data.password)
            
            # Create user document
            user_doc = {
                "email": user_data.email,
                "password_hash": password_hash,
                "role": user_data.role,
                "created_at": datetime.utcnow()
            }
            
            # Insert into database
            result = await self.collection.insert_one(user_doc)
            
            if result.inserted_id:
                created_user = await self.collection.find_one({"_id": result.inserted_id})
                
                user_response = UserResponse.from_mongo({
                    "_id": created_user["_id"],
                    "email": created_user["email"],
                    "role": created_user["role"],
                    "created_at": created_user["created_at"]
                })
                
                logger.info(f"User created successfully: {user_data.email}")
                return user_response
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        try:
            user_doc = await self.collection.find_one({"email": email})
            
            if user_doc:
                return UserResponse(
                    _id=str(user_doc["_id"]),
                    email=user_doc["email"],
                    role=user_doc["role"],
                    created_at=user_doc["created_at"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user by email: {str(e)}")
            return None
    
    async def initialize_admin_user(self):
        """Initialize default admin user if not exists"""
        try:
            admin_email = "focalisstrategagroup@gmail.com"
            admin_password = "FSG*2025"
            
            # Check if admin already exists
            existing_admin = await self.collection.find_one({"email": admin_email})
            
            if not existing_admin:
                admin_data = UserCreate(
                    email=admin_email,
                    password=admin_password,
                    role="admin"
                )
                
                admin_user = await self.create_user(admin_data)
                
                if admin_user:
                    logger.info("Default admin user created successfully")
                    return True
                else:
                    logger.error("Failed to create default admin user")
                    return False
            else:
                logger.info("Admin user already exists")
                return True
                
        except Exception as e:
            logger.error(f"Error initializing admin user: {str(e)}")
            return False