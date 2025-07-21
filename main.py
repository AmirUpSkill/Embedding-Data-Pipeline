import os
import requests
from dotenv import load_dotenv

# --- 1. Configuration & Setup ---
# Load environment variables from the .env file
load_dotenv()

# Get the API token from the environment. This is a secure way to handle secrets.
API_TOKEN = os.getenv("TMDB_API_READ_ACCESS_TOKEN")

# Define the API endpoint and the base URL for posters
API_ENDPOINT = "https://api.themoviedb.org/3/discover/movie"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# --- 2. Main Script Logic ---
def fetch_top_rated_movies():
    """
    Fetches the first page of top-rated movies from TMDB based on our contract.
    """
    # First, a critical check: did we load the API token correctly?
    if not API_TOKEN:
        print("❌ ERROR: TMDB_API_READ_ACCESS_TOKEN not found in .env file.")
        print("Please make sure you have a .env file with your token.")
        return

    # Define the headers for authentication, as required by the TMDB API
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }

    # Define the query parameters based on our expert discussion
    # This gives us high-quality results right from the source.
    params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "page": 1, # We only want the first page for this test (top 20 results)
        "sort_by": "vote_average.desc",
        "vote_count.gte": 200 # Filter out movies with too few votes
    }

    print("🚀 Attempting to fetch data from TMDB API...")
    print(f"   Endpoint: {API_ENDPOINT}")
    
    try:
        # Make the GET request to the API
        response = requests.get(API_ENDPOINT, headers=headers, params=params)

        # This will automatically raise an error for bad responses (4xx or 5xx)
        response.raise_for_status() 

        print("✅ Successfully connected to the API and received a response.")

        # Parse the JSON response into a Python dictionary
        data = response.json()
        movies = data.get("results", []) # Use .get() for safety in case 'results' is missing

        if not movies:
            print("🤔 No movies found in the response. Check your parameters.")
            return

        print("\n--- Top Movies Found (Page 1) ---")
        # --- 3. Display the Results ---
        # Loop through the movies and print the details in a clean format
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', 'N/A')
            release_date = movie.get('release_date', 'N/A')
            vote_average = movie.get('vote_average', 'N/A')
            poster_path = movie.get('poster_path', '')
            
            # Construct the full poster URL as we planned
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