from fastapi import APIRouter, Depends, Query
from typing import Optional

from controllers.diagnostico_controller import DiagnosticoController
from models.diagnostico import (
    DiagnosticoCreate, 
    DiagnosticoResponse, 
    DiagnosticoUpdate,
    DiagnosticoListResponse
)

# Create router
router = APIRouter(prefix="/diagnostico", tags=["Diagnostico Verde"])

# Initialize controller
controller = DiagnosticoController()

@router.post(
    "/", 
    response_model=DiagnosticoResponse,
    status_code=201,
    summary="Create Diagnostico Request",
    description="Submit a new green diagnosis request. This is a public endpoint."
)
async def create_diagnostico(diagnostico_data: DiagnosticoCreate):
    """
    Create a new diagnostico verde request.
    
    - **empresa**: Company name (required)
    - **contacto_nombre**: Contact person name (required)  
    - **contacto_email**: Contact email (required)
    - **telefono**: Phone number (optional)
    - **mensaje**: Additional message (optional)
    - **sector**: Industry sector (optional)
    - **fuente_trafico**: Traffic source (default: web)
    """
    return await controller.create_diagnostico(diagnostico_data)

@router.get(
    "/", 
    response_model=DiagnosticoListResponse,
    summary="List Diagnosticos",
    description="Get paginated list of diagnostico requests. Admin access required."
)
async def get_diagnosticos_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    estado: Optional[str] = Query(None, description="Filter by status (pendiente, en_proceso, completado, cancelado)"),
    admin_token: dict = Depends(controller.verify_admin_token)
):
    """
    Get a paginated list of all diagnostico requests.
    
    **Query Parameters:**
    - **page**: Page number (starts at 1)
    - **limit**: Number of items per page (max 100)
    - **estado**: Filter by status (optional)
    
    **Requires:** Admin authentication
    """
    return await controller.get_diagnosticos_list(page, limit, estado, admin_token)

@router.get(
    "/{diagnostico_id}", 
    response_model=DiagnosticoResponse,
    summary="Get Diagnostico by ID",
    description="Get specific diagnostico request by ID. Admin access required."
)
async def get_diagnostico_by_id(
    diagnostico_id: str,
    admin_token: dict = Depends(controller.verify_admin_token)
):
    """
    Get a specific diagnostico request by its ID.
    
    **Path Parameters:**
    - **diagnostico_id**: The ID of the diagnostico request
    
    **Requires:** Admin authentication
    """
    return await controller.get_diagnostico_by_id(diagnostico_id, admin_token)

@router.put(
    "/{diagnostico_id}", 
    response_model=DiagnosticoResponse,
    summary="Update Diagnostico",
    description="Update diagnostico request. Admin access required."
)
async def update_diagnostico(
    diagnostico_id: str,
    update_data: DiagnosticoUpdate,
    admin_token: dict = Depends(controller.verify_admin_token)
):
    """
    Update a diagnostico request.
    
    **Path Parameters:**
    - **diagnostico_id**: The ID of the diagnostico request
    
    **Body:** Only provided fields will be updated
    - **estado**: Change status
    - **sector**: Update industry sector
    
    **Requires:** Admin authentication
    """
    return await controller.update_diagnostico(diagnostico_id, update_data, admin_token)

@router.delete(
    "/{diagnostico_id}",
    summary="Delete Diagnostico", 
    description="Delete diagnostico request. Admin access required."
)
async def delete_diagnostico(
    diagnostico_id: str,
    admin_token: dict = Depends(controller.verify_admin_token)
):
    """
    Delete a diagnostico request.
    
    **Path Parameters:**
    - **diagnostico_id**: The ID of the diagnostico request
    
    **Requires:** Admin authentication
    """
    return await controller.delete_diagnostico(diagnostico_id, admin_token)

@router.get(
    "/analytics/dashboard",
    summary="Get Analytics Data",
    description="Get analytics and metrics data. Admin access required."
)
async def get_analytics(
    admin_token: dict = Depends(controller.verify_admin_token)
):
    """
    Get analytics data for the admin dashboard.
    
    Returns:
    - Total number of requests
    - Recent activity (last 30 days)
    - Breakdown by status
    - Breakdown by traffic source
    
    **Requires:** Admin authentication
    """
    return await controller.get_analytics(admin_token)