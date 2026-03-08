import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration with fallback
SUPABASE_URL = "postgresql://chat_backend:OfflineChatBack%402026@db.rzizabevumuzxkxanzow.supabase.co:5432/postgres?sslmode=require"
SQLITE_URL = "sqlite:///./sql_app.db"

try:
    print("Connecting to Supabase...")
    engine = create_engine(SUPABASE_URL, connect_args={"connect_timeout": 5})
    # Force a connection test
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("SELECT 1"))
    print("  Connected to Supabase successfully!")
except Exception as e:
    print(f"  Supabase connection failed ({e}). Falling back to local SQLite.")
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
