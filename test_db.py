
import sqlalchemy
from sqlalchemy import create_engine

def test_connection(url):
    print(f"Testing URL: {url.split('@')[1] if '@' in url else url}")
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT 1"))
            print("  SUCCESS!")
            return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

# Variant 1: Current (escaped)
url1 = "postgresql://postgres:Internalmarks%4025@db.rzizabevumuzxkxanzow.supabase.co:6543/postgres?sslmode=require"
# Variant 2: Unescaped
url2 = "postgresql://postgres:Internalmarks@25@db.rzizabevumuzxkxanzow.supabase.co:6543/postgres?sslmode=require"
# Variant 3: Direct port 5432
url3 = "postgresql://postgres:Internalmarks%4025@db.rzizabevumuzxkxanzow.supabase.co:5432/postgres?sslmode=require"

print("Starting connection tests...")
test_connection(url1)
test_connection(url2)
test_connection(url3)
