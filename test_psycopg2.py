
import psycopg2
import urllib.parse

# The password as it appears in the URI is Internalmarks%4025
# Which means the actual password is Internalmarks@25
pass_raw = "Internalmarks@25"
pass_encoded = urllib.parse.quote_plus(pass_raw)

print(f"Raw password: {pass_raw}")
print(f"Encoded password: {pass_encoded}")

dsn = "postgresql://postgres:Internalmarks@25@db.rzizabevumuzxkxanzow.supabase.co:5432/postgres?sslmode=require"
dsn_escaped = f"postgresql://postgres:{pass_encoded}@db.rzizabevumuzxkxanzow.supabase.co:5432/postgres?sslmode=require"

def test_dsn(name, dsn_str):
    print(f"Testing {name}...")
    try:
        conn = psycopg2.connect(dsn_str)
        print("  SUCCESS!")
        conn.close()
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

test_dsn("Unescaped Port 5432", dsn)
test_dsn("Escaped Port 5432", dsn_escaped)

# Try with 6543
dsn_6543 = dsn_escaped.replace(":5432", ":6543")
test_dsn("Escaped Port 6543", dsn_6543)
