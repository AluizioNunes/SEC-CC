from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# Database URLs
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/sec_cadastro")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# SQLAlchemy setup for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Dependency to get DB session
async def get_db():
    async with async_session() as session:
        yield session
