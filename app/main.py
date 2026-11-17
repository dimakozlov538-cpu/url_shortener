import os
import string
import random
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="DevOps URL Shortener")
Instrumentator().instrument(app).expose(app)

# Настройки из переменных окружения
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/shortener")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_db():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

@app.on_event("startup")
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id SERIAL PRIMARY KEY,
            short_code VARCHAR(10) UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

class URLRequest(BaseModel):
    url: HttpUrl

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.get("/health")
def health_check():
    try:
        r.ping()
        conn = get_db()
        conn.close()
        return {"status": "healthy", "database": "ok", "redis": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/shorten")
def create_short_url(req: URLRequest):
    code = generate_code()
    original = str(req.url)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO urls (short_code, original_url) VALUES (%s, %s) RETURNING short_code;",
        (code, original)
    )
    conn.commit()
    cur.close()
    conn.close()
    r.setex(f"url:{code}", 3600, original)
    return {"short_code": code, "short_url": f"http://localhost:8000/{code}"}

@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    # 1. Сначала ищем в быстром кэше Redis
    cached_url = r.get(f"url:{short_code}")
    conn = get_db()
    cur = conn.cursor()

    if cached_url:
        cur.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s;", (short_code,))
        conn.commit()
        cur.close()
        conn.close()
        return RedirectResponse(url=cached_url)

    # 2. Если в кэше нет — идем в PostgreSQL
    cur.execute("SELECT original_url FROM urls WHERE short_code = %s;", (short_code,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="URL not found")

    cur.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s;", (short_code,))
    conn.commit()
    cur.close()
    conn.close()

    r.setex(f"url:{short_code}", 3600, row["original_url"])
    return RedirectResponse(url=row["original_url"])

@app.get("/stats/{short_code}")
def get_stats(short_code: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT short_code, original_url, clicks, created_at FROM urls WHERE short_code = %s;", (short_code,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="URL not found")
    return row
