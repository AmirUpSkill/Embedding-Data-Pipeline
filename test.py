import os
import requests
from dotenv import load_dotenv

# Config
load_dotenv()
API_TOKEN = os.getenv("TMDB_API_READ_ACCESS_TOKEN")
API_ENDPOINT = "https://api.themoviedb.org/3/discover/movie"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

def fetch_top_rated_movies():
    """Get top rated movies from TMDB API"""
    
    if not API_TOKEN:
        print("❌ ERROR: TMDB_API_READ_ACCESS_TOKEN not found in .env file.")
        print("Please make sure you have a .env file with your token.")
        return

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }

    params = {
        "include_adult": "false",
        "include_video": "false", 
        "language": "en-US",
        "page": 1,
        "sort_by": "vote_average.desc",
        "vote_count.gte": 200
    }

    print("🚀 Attempting to fetch data from TMDB API...")
    print(f"   Endpoint: {API_ENDPOINT}")
    
    try:
        response = requests.get(API_ENDPOINT, headers=headers, params=params)
        response.raise_for_status()
        print("✅ Successfully connected to the API and received a response.")

        data = response.json()
        movies = data.get("results", [])

        if not movies:
            print("🤔 No movies found in the response. Check your parameters.")
            return

        print("\n--- Top Movies Found (Page 1) ---")
        
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', 'N/A')
            release_date = movie.get('release_date', 'N/A')
            vote_average = movie.get('vote_average', 'N/A')
            poster_path = movie.get('poster_path', '')
            
            full_poster_url = f"{POSTER_BASE_URL}{poster_path}" if poster_path else "No Poster"

            print(f"\n{i}. {title}")
            print(f"   Release Date: {release_date}")
            print(f"   Vote Average: {vote_average} ⭐")
            # print(f"   Poster URL: {full_poster_url}") # Optional: uncomment to see the full URL

    except requests.exceptions.RequestException as e:
        print(f"\n❌ An error occurred during the API request: {e}")
    except KeyError as e:
        print(f"\n❌ An error occurred parsing the response data. Missing key: {e}")


if __name__ == "__main__":
    fetch_top_rated_movies()