from fastapi import HTTPException, status
import logging

from services.auth_service import AuthService
from models.user import UserLogin, TokenResponse

logger = logging.getLogger(__name__)

class AuthController:
    def __init__(self):
        self.service = AuthService()
    
    async def login(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return access token"""
        try:
            result = await self.service.authenticate_user(login_data)
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in login controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def initialize_admin(self) -> dict:
        """Initialize default admin user (development only)"""
        try:
            success = await self.service.initialize_admin_user()
            
            if success:
                return {
                    "message": "Admin user initialized successfully",
                    "email": "focalisstrategagroup@gmail.com",
                    "password": "FSG*2025"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to initialize admin user"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in initialize_admin controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )