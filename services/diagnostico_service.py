from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import logging

from config.database import get_diagnostico_collection
from models.diagnostico import (
    DiagnosticoCreate, 
    DiagnosticoResponse, 
    DiagnosticoUpdate, 
    EstadoDiagnostico,
    DiagnosticoListResponse
)
from utils.validators import (
    validate_phone_number, 
    validate_email_domain, 
    validate_company_name,
    validate_contact_name,
    sanitize_text_input
)
from utils.notifications import send_notification

logger = logging.getLogger(__name__)

class DiagnosticoService:
    def __init__(self):
        self.collection = get_diagnostico_collection()
    
    async def create_diagnostico(self, diagnostico_data: DiagnosticoCreate) -> DiagnosticoResponse:
        """Create a new diagnostico request"""
        try:
            # Validate and sanitize inputs
            validated_data = {
                "empresa": validate_company_name(diagnostico_data.empresa),
                "contacto_nombre": validate_contact_name(diagnostico_data.contacto_nombre),
                "contacto_email": diagnostico_data.contacto_email,
                "telefono": validate_phone_number(diagnostico_data.telefono),
                "mensaje": sanitize_text_input(diagnostico_data.mensaje),
                "sector": sanitize_text_input(diagnostico_data.sector, 100),
                "fuente_trafico": diagnostico_data.fuente_trafico,
                "estado": EstadoDiagnostico.PENDIENTE,
                "fecha_solicitud": datetime.utcnow()
            }
            
            # Additional email validation
            if not validate_email_domain(diagnostico_data.contacto_email):
                logger.warning(f"Potentially disposable email used: {diagnostico_data.contacto_email}")
            
            # Insert into database
            result = await self.collection.insert_one(validated_data)
            
            if result.inserted_id:
                # Fetch the created document
                created_doc = await self.collection.find_one({"_id": result.inserted_id})
                
                # Send notification asynchronously
                try:
                    await send_notification(validated_data)
                except Exception as e:
                    logger.error(f"Failed to send notification: {str(e)}")
                    # Don't fail the request if notification fails
                
                logger.info(f"Created diagnostico for {validated_data['empresa']}")
                return DiagnosticoResponse.from_mongo(created_doc)
            
            else:
                raise Exception("Failed to create diagnostico")
                
        except Exception as e:
            logger.error(f"Error creating diagnostico: {str(e)}")
            raise e
    
    async def get_diagnostico_by_id(self, diagnostico_id: str) -> Optional[DiagnosticoResponse]:
        """Get diagnostico by ID"""
        try:
            if not ObjectId.is_valid(diagnostico_id):
                return None
            
            doc = await self.collection.find_one({"_id": ObjectId(diagnostico_id)})
            
            if doc:
                return DiagnosticoResponse.from_mongo(doc)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching diagnostico {diagnostico_id}: {str(e)}")
            return None
    
    async def get_diagnosticos_list(
        self, 
        page: int = 1, 
        limit: int = 50, 
        estado: Optional[str] = None
    ) -> DiagnosticoListResponse:
        """Get paginated list of diagnosticos"""
        try:
            # Build query
            query = {}
            if estado:
                query["estado"] = estado
            
            # Calculate skip
            skip = (page - 1) * limit
            
            # Get total count
            total = await self.collection.count_documents(query)
            
            # Get documents
            cursor = self.collection.find(query).sort("fecha_solicitud", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            diagnosticos = [DiagnosticoResponse.from_mongo(doc) for doc in docs]
            
            has_more = (skip + limit) < total
            
            return DiagnosticoListResponse(
                diagnosticos=diagnosticos,
                total=total,
                page=page,
                limit=limit,
                has_more=has_more
            )
            
        except Exception as e:
            logger.error(f"Error fetching diagnosticos list: {str(e)}")
            raise e
    
    async def update_diagnostico(
        self, 
        diagnostico_id: str, 
        update_data: DiagnosticoUpdate
    ) -> Optional[DiagnosticoResponse]:
        """Update diagnostico"""
        try:
            if not ObjectId.is_valid(diagnostico_id):
                return None
            
            update_dict = {}
            if update_data.estado:
                update_dict["estado"] = update_data.estado
            if update_data.sector:
                update_dict["sector"] = sanitize_text_input(update_data.sector, 100)
            
            if not update_dict:
                return await self.get_diagnostico_by_id(diagnostico_id)
            
            result = await self.collection.update_one(
                {"_id": ObjectId(diagnostico_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return await self.get_diagnostico_by_id(diagnostico_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating diagnostico {diagnostico_id}: {str(e)}")
            return None
    
    async def delete_diagnostico(self, diagnostico_id: str) -> bool:
        """Delete diagnostico"""
        try:
            if not ObjectId.is_valid(diagnostico_id):
                return False
            
            result = await self.collection.delete_one({"_id": ObjectId(diagnostico_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted diagnostico {diagnostico_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting diagnostico {diagnostico_id}: {str(e)}")
            return False
    
    async def get_analytics_data(self) -> dict:
        """Get analytics data for dashboard"""
        try:
            # Total requests
            total_requests = await self.collection.count_documents({})
            
            # Requests by status
            status_pipeline = [
                {"$group": {"_id": "$estado", "count": {"$sum": 1}}}
            ]
            status_data = await self.collection.aggregate(status_pipeline).to_list(None)
            
            # Requests by traffic source
            traffic_pipeline = [
                {"$group": {"_id": "$fuente_trafico", "count": {"$sum": 1}}}
            ]
            traffic_data = await self.collection.aggregate(traffic_pipeline).to_list(None)
            
            # Recent activity (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_requests = await self.collection.count_documents({
                "fecha_solicitud": {"$gte": thirty_days_ago}
            })
            
            return {
                "total_requests": total_requests,
                "recent_requests": recent_requests,
                "by_status": {item["_id"]: item["count"] for item in status_data},
                "by_traffic_source": {item["_id"]: item["count"] for item in traffic_data}
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return {}