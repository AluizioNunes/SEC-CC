from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from database import Base

class SECUsuario(Base):
    __tablename__ = "Usuario"
    __table_args__ = {"schema": "SEC"}

    IdUsuario = Column(BigInteger, primary_key=True, index=True)
    Nome = Column(String(255), nullable=False)
    Funcao = Column(String(255))
    Departamento = Column(String(255))
    Lotacao = Column(String(255))
    Perfil = Column(String(100))
    Permissao = Column(String(100))
    Email = Column(String(255), unique=True)
    Usuario = Column(String(100), unique=True)
    Senha = Column(String(255))
    DataCadastro = Column(DateTime(timezone=True), server_default=func.now())
    Cadastrante = Column(String(255))
    Image = Column(String(1024))
    DataUpdate = Column(DateTime(timezone=True))
    TipoUpdate = Column(String(100))
    Observacao = Column(Text)
