from typing import Optional
from fastapi import HTTPException, status, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from services.diagnostico_service import DiagnosticoService
from models.diagnostico import (
    DiagnosticoCreate, 
    DiagnosticoResponse, 
    DiagnosticoUpdate,
    DiagnosticoListResponse
)
from config.auth import verify_token

logger = logging.getLogger(__name__)
security = HTTPBearer()

class DiagnosticoController:
    def __init__(self):
        self.service = DiagnosticoService()
    
    async def verify_admin_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify admin token for protected endpoints"""
        try:
            payload = verify_token(credentials.credentials)
            
            if payload.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            return payload
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
    
    async def create_diagnostico(self, diagnostico_data: DiagnosticoCreate) -> DiagnosticoResponse:
        """Create new diagnostico request (public endpoint)"""
        try:
            result = await self.service.create_diagnostico(diagnostico_data)
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create diagnostico request"
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in create_diagnostico controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_diagnostico_by_id(
        self, 
        diagnostico_id: str,
        admin_token: dict = Depends(verify_admin_token)
    ) -> DiagnosticoResponse:
        """Get diagnostico by ID (admin only)"""
        try:
            result = await self.service.get_diagnostico_by_id(diagnostico_id)
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Diagnostico not found"
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_diagnostico_by_id controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_diagnosticos_list(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(50, ge=1, le=100, description="Items per page"),
        estado: Optional[str] = Query(None, description="Filter by status"),
        admin_token: dict = Depends(verify_admin_token)
    ) -> DiagnosticoListResponse:
        """Get paginated list of diagnosticos (admin only)"""
        try:
            result = await self.service.get_diagnosticos_list(page, limit, estado)
            return result
            
        except Exception as e:
            logger.error(f"Error in get_diagnosticos_list controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def update_diagnostico(
        self,
        diagnostico_id: str,
        update_data: DiagnosticoUpdate,
        admin_token: dict = Depends(verify_admin_token)
    ) -> DiagnosticoResponse:
        """Update diagnostico (admin only)"""
        try:
            result = await self.service.update_diagnostico(diagnostico_id, update_data)
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Diagnostico not found"
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in update_diagnostico controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def delete_diagnostico(
        self,
        diagnostico_id: str,
        admin_token: dict = Depends(verify_admin_token)
    ) -> dict:
        """Delete diagnostico (admin only)"""
        try:
            success = await self.service.delete_diagnostico(diagnostico_id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Diagnostico not found"
                )
            
            return {"message": "Diagnostico deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in delete_diagnostico controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_analytics(
        self,
        admin_token: dict = Depends(verify_admin_token)
    ) -> dict:
        """Get analytics data (admin only)"""
        try:
            result = await self.service.get_analytics_data()
            return result
            
        except Exception as e:
            logger.error(f"Error in get_analytics controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )