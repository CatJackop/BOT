import os
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase): pass
def url():
 u=os.getenv("DATABASE_URL","sqlite+aiosqlite:///./catjack.db")
 return "postgresql+asyncpg://"+u[11:] if u.startswith("postgres://") else ("postgresql+asyncpg://"+u[13:] if u.startswith("postgresql://") else u)
engine=create_async_engine(url(),pool_pre_ping=True)
SessionLocal=async_sessionmaker(engine,expire_on_commit=False,class_=AsyncSession)
async def init_db():
 from .models import GuildSettings
 async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
def get_session(): return SessionLocal()
