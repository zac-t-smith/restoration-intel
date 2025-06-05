from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "postgresql://postgres:Zak350$!*@db.ieuawvhdpfhunvqsfznq.supabase.co:5432/postgres"
JWT_SECRET = os.getenv("hnK3FUqtvtrkHDPokTEmaH46HWU5FoWSL06HupYwpSsLNH5GFjSRpzkRU8hhlRaa8srpvAqO8mFlFwyja0AYxA==")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 