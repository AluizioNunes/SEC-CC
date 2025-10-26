from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URLs
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sec:secpass2024@localhost:5432/secdb")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27018/secmongo")

# SQLAlchemy setup for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Dependency to get DB session
async def get_db():
    async with async_session() as session:
        yield session
