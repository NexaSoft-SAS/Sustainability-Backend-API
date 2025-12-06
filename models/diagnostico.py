from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class EstadoDiagnostico(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"

class FuenteTrafico(str, Enum):
    WEB = "web"
    LINKEDIN = "linkedin"
    EMAIL = "email"
    REFERENCIA = "referencia"
    DIRECTO = "directo"
    OTROS = "otros"

class DiagnosticoCreate(BaseModel):
    """Schema for creating a new diagnostico request"""
    empresa: str = Field(..., min_length=2, max_length=200, description="Company name")
    contacto_nombre: str = Field(..., min_length=2, max_length=100, description="Contact person name")
    contacto_email: EmailStr = Field(..., description="Contact email")
    telefono: Optional[str] = Field(None, max_length=20, description="Phone number")
    mensaje: Optional[str] = Field(None, max_length=1000, description="Additional message")
    sector: Optional[str] = Field(None, max_length=100, description="Industry sector")
    fuente_trafico: FuenteTrafico = Field(default=FuenteTrafico.WEB, description="Traffic source")

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "empresa": "EcoTech Solutions",
                "contacto_nombre": "Juan Pérez",
                "contacto_email": "juan@ecotech.com",
                "telefono": "+34 600 123 456",
                "mensaje": "Interesados en reducir nuestra huella de carbono",
                "sector": "Tecnología",
                "fuente_trafico": "web"
            }
        }

class DiagnosticoResponse(BaseModel):
    """Schema for diagnostico response"""
    id: str = Field(alias="_id")
    empresa: str
    contacto_nombre: str
    contacto_email: str
    telefono: Optional[str] = None
    mensaje: Optional[str] = None
    sector: Optional[str] = None
    fuente_trafico: str
    estado: EstadoDiagnostico
    fecha_solicitud: datetime
    
    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB document to response model"""
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        use_enum_values = True

class DiagnosticoUpdate(BaseModel):
    """Schema for updating diagnostico"""
    estado: Optional[EstadoDiagnostico] = None
    sector: Optional[str] = None
    
    class Config:
        use_enum_values = True

class DiagnosticoListResponse(BaseModel):
    """Schema for diagnostico list with pagination"""
    diagnosticos: list[DiagnosticoResponse]
    total: int
    page: int
    limit: int
    has_more: bool