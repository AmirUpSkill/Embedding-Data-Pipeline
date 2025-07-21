import dlt
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator
from dlt.sources.rest_api import rest_api_source

@dlt.source(name="tmdb_discover")
def tmdb_source(
    api_token: str = dlt.secrets.value,
    max_pages: int = 2 # We will fetch exactly 2 pages
):
    """
    A dlt source that fetches movie data from the TMDB API.

    This source defines one resource corresponding to the /discover/movie
    endpoint and applies the precise API contract we designed.

    Args:
        api_token: The TMDB API Read Access Token, injected by dlt from secrets.
        max_pages: The total number of pages to fetch.
    """
    paginator = PageNumberPaginator(
        page_param="page",          # The query param for page number is 'page'
        total_path="total_pages",   # The API tells us the total pages here
        maximum_page=max_pages,     # We instruct the paginator to stop after max_pages
        base_page=1                 # TMDB API pages start from 1, not 0
    )

    # This configuration dictionary IS our API Contract implemented in code.
    movies_resource = rest_api_source({
        "client": {
            "base_url": "https://api.themoviedb.org/3/",
            "auth": {
                "token": api_token
            },
            "paginator": paginator,
        },
        "resources": [
            {
                # This will become the table name in Postgres
                "name": "raw_movies",
                # Best practice: define a primary key for future merging
                "primary_key": "id",
                # We will merge data based on the primary key
                "write_disposition": "merge",
                "endpoint": {
                    "path": "discover/movie",
                    "params": {
                        "include_adult": "false",
                        "language": "en-US",
                        # --- Our Established Contract ---
                        "sort_by": "vote_average.desc", # Get best-rated first
                        "vote_count.gte": 200,          # Ensure quality with min votes
                    },
                    # Tell dlt where to find the list of data in the response
                    "data_selector": "results",
                },
            }
        ],
    })

    return movies_resource

# --- Main Execution Block ---
if __name__ == "__main__":
    print("🚀 Starting the TMDB Extract & Load pipeline...")

    # Configure and create the pipeline
    pipeline = dlt.pipeline(
        pipeline_name="tmdb_raw_discover",
        destination="postgres",
        dataset_name="tmdb_data" # This will become the PostgreSQL schema name
    )

    # Create an instance of the source, fetching 2 pages
    source_data = tmdb_source(max_pages=2)

    # Run the pipeline to extract and load the data
    load_info = pipeline.run(source_data)

    # Print the outcome of the load
    print("✅ Pipeline run finished!")
    print(load_info)