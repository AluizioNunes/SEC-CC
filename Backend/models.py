from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, BigInteger
from sqlalchemy.sql import func
from database import Base
import enum

class UserType(str, enum.Enum):
    individual = "individual"
    entity = "entity"

class RegistrationStatus(str, enum.Enum):
    new = "new"
    under_review = "under_review"
    in_diligence = "in_diligence"
    approved = "approved"
    rejected = "rejected"
    suspended = "suspended"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    user_type = Column(Enum(UserType))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IndividualRegistration(Base):
    __tablename__ = "individual_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    cpf = Column(String, unique=True, index=True)
    birth_date = Column(DateTime)
    nationality = Column(String)
    rg_document = Column(String)
    rg_number = Column(String)
    rg_issuer = Column(DateTime)
    address_cep = Column(String)
    address_street = Column(String)
    address_number = Column(String)
    address_complement = Column(String)
    address_neighborhood = Column(String)
    address_city = Column(String)
    address_state = Column(String, default="Amazonas")
    cultural_areas = Column(Text)  # JSON string of areas
    portfolio_url = Column(String)
    proof_experience = Column(Text)  # JSON string of proofs
    status = Column(Enum(RegistrationStatus), default=RegistrationStatus.new)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EntityRegistration(Base):
    __tablename__ = "entity_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    company_name = Column(String)
    fantasy_name = Column(String)
    cnpj = Column(String, unique=True, index=True)
    cultural_space_types = Column(Text)  # JSON string of types
    address_cep = Column(String)
    address_street = Column(String)
    address_number = Column(String)
    address_complement = Column(String)
    address_neighborhood = Column(String)
    address_city = Column(String)
    address_state = Column(String, default="Amazonas")
    legal_representative_name = Column(String)
    legal_representative_cpf = Column(String)
    legal_representative_email = Column(String)
    portfolio_url = Column(String)
    proof_experience = Column(Text)  # JSON string of proofs
    status = Column(Enum(RegistrationStatus), default=RegistrationStatus.new)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, index=True)  # Can be individual or entity
    registration_type = Column(String)  # "individual" or "entity"
    file_name = Column(String)
    file_path = Column(String)  # Path in MongoDB or file system
    document_type = Column(String)  # e.g., "proof_of_residence", "portfolio"
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class SECUsuario(Base):
    __tablename__ = "Usuarios"
    __table_args__ = {"schema": "SEC"}

    IdUsuario = Column(BigInteger, primary_key=True, index=True)
    Nome = Column(String(255), nullable=False)
    Funcao = Column(String(255))
    Departamento = Column(String(255))
    Lotacao = Column(String(255))
    Perfil = Column(String(100))
    Permissao = Column(String(100))
    Email = Column(String(255), unique=True)
    Login = Column(String(100), unique=True)
    Senha = Column(String(255))
    DataCadastro = Column(DateTime(timezone=True), server_default=func.now())
    Cadastrante = Column(String(255))
    Image = Column(String(1024))
    DataUpdate = Column(DateTime(timezone=True))
    TipoUpdate = Column(String(100))
    Observacao = Column(Text)
