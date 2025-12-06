from fastapi import APIRouter

from controllers.auth_controller import AuthController
from models.user import UserLogin, TokenResponse

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize controller
controller = AuthController()

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Admin Login",
    description="Authenticate admin user and get access token"
)
async def login(login_data: UserLogin):
    """
    Authenticate admin user and return JWT access token.
    
    **Default Admin Credentials:**
    - **email**: focalisstrategagroup@gmail.com
    - **password**: FSG*2025
    
    **Returns:**
    - Access token (valid for 24 hours)
    - Token type (bearer)
    - User information
    """
    return await controller.login(login_data)

@router.post(
    "/initialize-admin",
    summary="Initialize Admin User",
    description="Create default admin user (development only)"
)
async def initialize_admin():
    """
    Initialize the default admin user for development/testing.
    
    Creates admin user with:
    - Email: focalisstrategagroup@gmail.com  
    - Password: FSG*2025
    - Role: admin
    
    **Note:** This endpoint is for development purposes only.
    In production, admin users should be created through a secure process.
    """
    return await controller.initialize_admin()