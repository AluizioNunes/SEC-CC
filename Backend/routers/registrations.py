from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import IndividualRegistration, User, Document

router = APIRouter()

# Pydantic models for request/response
class IndividualRegistrationCreate(BaseModel):
    full_name: str
    cpf: str
    birth_date: str  # ISO format date
    nationality: str
    rg_document_type: str
    rg_number: str
    rg_issuer: str
    address_cep: str
    address_street: str
    address_number: str
    address_complement: Optional[str] = None
    address_neighborhood: str
    address_city: str
    address_state: str = "Amazonas"
    cultural_areas: str  # Comma-separated string
    portfolio_url: Optional[str] = None
    experience_description: str

    @validator('cpf')
    def validate_cpf(cls, v):
        # Basic CPF validation (can be enhanced)
        if len(v.replace('.', '').replace('-', '')) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return v

class IndividualRegistrationResponse(BaseModel):
    id: int
    user_id: int
    cpf: str
    status: str
    created_at: datetime

@router.post("/individual", response_model=IndividualRegistrationResponse)
async def create_individual_registration(
    registration_data: IndividualRegistrationCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Uncomment when auth is ready
):
    # Check if CPF already exists
    result = await db.execute(select(IndividualRegistration).where(IndividualRegistration.cpf == registration_data.cpf))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # For now, create a mock user_id (replace with actual user from auth)
    user_id = 1  # This should come from authenticated user
    
    # Create registration
    new_registration = IndividualRegistration(
        user_id=user_id,
        cpf=registration_data.cpf,
        birth_date=datetime.fromisoformat(registration_data.birth_date),
        nationality=registration_data.nationality,
        rg_document=registration_data.rg_document_type,
        rg_number=registration_data.rg_number,
        rg_issuer=registration_data.rg_issuer,
        address_cep=registration_data.address_cep,
        address_street=registration_data.address_street,
        address_number=registration_data.address_number,
        address_complement=registration_data.address_complement,
        address_neighborhood=registration_data.address_neighborhood,
        address_city=registration_data.address_city,
        address_state=registration_data.address_state,
        cultural_areas=registration_data.cultural_areas,
        portfolio_url=registration_data.portfolio_url,
        proof_experience=registration_data.experience_description
    )
    
    db.add(new_registration)
    await db.commit()
    await db.refresh(new_registration)
    
    return new_registration

@router.post("/individual/{registration_id}/documents")
async def upload_individual_documents(
    registration_id: int,
    files: List[UploadFile] = File(...),
    document_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    # Verify registration exists
    result = await db.execute(select(IndividualRegistration).where(IndividualRegistration.id == registration_id))
    registration = result.scalar_one_or_none()
    if not registration:
        raise HTTPException(status_code=404, detail="Cadastro não encontrado")
    
    uploaded_docs = []
    for file in files:
        # Here you would typically save the file to MongoDB or a file storage service
        # For now, just create a document record
        doc = Document(
            registration_id=registration_id,
            registration_type="individual",
            file_name=file.filename,
            file_path=f"/uploads/{registration_id}/{file.filename}",  # Mock path
            document_type=document_type or "general"
        )
        db.add(doc)
        uploaded_docs.append({"filename": file.filename, "type": document_type})
    
    await db.commit()
    return {"message": "Documentos enviados com sucesso", "documents": uploaded_docs}

@router.get("/individual", response_model=List[IndividualRegistrationResponse])
async def list_individual_registrations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(IndividualRegistration).offset(skip).limit(limit)
    )
    registrations = result.scalars().all()
    return registrations
