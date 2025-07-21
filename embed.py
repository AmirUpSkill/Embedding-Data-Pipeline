import os
import psycopg2
import psycopg2.extras
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm
from datetime import datetime

# Init script
print("🚀 Initializing Transformation Script...")

# Env setup
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ ERROR: GOOGLE_API_KEY not found in .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# DB config
DB_PARAMS = {
    "dbname": "cinemax_db",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
EMBEDDING_MODEL = "models/embedding-001" # Gemini API model

def fetch_raw_movies(conn):
    """Fetch movies from staging table"""
    print("📖 Fetching raw movie data from the staging table...")
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute("""
            SELECT id, title, overview, poster_path, release_date, vote_average
            FROM tmdb_data.raw_movies;
        """)
        movies = cursor.fetchall()
        print(f"✅ Found {len(movies)} movies to process.")
        return movies

def transform_and_embed_batch(movies_raw):
    """Transform data and generate embeddings"""
    print("✨ Preparing batch for transformation and embedding...")
    texts_to_embed = []
    transformed_movies = []

    for movie in movies_raw:
        # Transform movie data
        title = movie['title'] or ""
        overview = movie['overview'] or "No overview available."

        release_year = None
        if movie['release_date']:
            try:
                release_year = datetime.strptime(movie['release_date'], '%Y-%m-%d').year
            except (ValueError, TypeError):
                release_year = None

        rating = round(movie['vote_average'], 1) if movie['vote_average'] is not None else 0.0
        poster_url = f"{POSTER_BASE_URL}{movie['poster_path']}" if movie['poster_path'] else None

        # Prep embedding text
        semantic_text = f"Movie Title: {title}. Overview: {overview}"
        texts_to_embed.append(semantic_text)

        transformed_movies.append({
            "id": movie['id'],
            "title": title,
            "overview": overview,
            "release_year": release_year,
            "rating": rating,
            "poster_url": poster_url,
        })

    print(f"🤖 Calling Gemini API to generate embeddings for {len(texts_to_embed)} movies...")
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=texts_to_embed,
        task_type="RETRIEVAL_DOCUMENT",
    )

    embeddings = result['embedding']

    for i, movie in enumerate(transformed_movies):
        movie['embedding'] = embeddings[i]

    print("✅ Successfully generated and combined embeddings.")
    return transformed_movies

def upsert_production_movies(conn, transformed_movies):
    """Upsert movies to production table"""
    print(f"💾 Upserting {len(transformed_movies)} movies into the production table...")
    with conn.cursor() as cursor:
        upsert_query = """
            INSERT INTO public.movies_production (id, title, overview, release_year, rating, poster_url, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                overview = EXCLUDED.overview,
                release_year = EXCLUDED.release_year,
                rating = EXCLUDED.rating,
                poster_url = EXCLUDED.poster_url,
                embedding = EXCLUDED.embedding;
        """
        for movie in tqdm(transformed_movies, desc="Upserting movies"):
            cursor.execute(upsert_query, (
                movie['id'],
                movie['title'],
                movie['overview'],
                movie['release_year'],
                movie['rating'],
                movie['poster_url'],
                movie['embedding']
            ))
        conn.commit()
        print("✅ All movies have been successfully saved to the production table.")

def create_production_table(conn):
    """Setup production table and vector extension"""
    with conn.cursor() as cursor:
        print("🔍 Checking for pgvector extension and production table...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public.movies_production (
                id BIGINT PRIMARY KEY,
                title TEXT NOT NULL,
                overview TEXT,
                release_year INTEGER,
                rating REAL,
                poster_url TEXT,
                embedding VECTOR(768)
            );
        """)
        conn.commit()
        print("✅ Database is ready.")

if __name__ == "__main__":
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("🔗 Database connection established.")

        create_production_table(conn)
        raw_movies = fetch_raw_movies(conn)

        if raw_movies:
            transformed_movies = transform_and_embed_batch(raw_movies)
            upsert_production_movies(conn, transformed_movies)
        else:
            print("No new movies to process.")

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("📦 Database connection closed.")