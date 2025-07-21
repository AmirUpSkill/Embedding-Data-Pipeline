import dlt
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator
from dlt.sources.rest_api import rest_api_source

@dlt.source(name="tmdb_discover")
def tmdb_source(
    api_token: str = dlt.secrets.value,
    max_pages: int = 2 # pages to fetch
):
    """
    TMDB API movie data source
    """
    paginator = PageNumberPaginator(
        page_param="page",      # page param
        total_path="total_pages", 
        maximum_page=max_pages,  
        base_page=1            # start at 1
    )

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
                "name": "raw_movies",
                "primary_key": "id",
                "write_disposition": "merge",
                "endpoint": {
                    "path": "discover/movie",
                    "params": {
                        "include_adult": "false",
                        "language": "en-US",
                        "sort_by": "vote_average.desc", # best rated first
                        "vote_count.gte": 200,          # min votes
                    },
                    "data_selector": "results",
                },
            }
        ],
    })

    return movies_resource

if __name__ == "__main__":
    print("🚀 Starting the TMDB Extract & Load pipeline...")

    pipeline = dlt.pipeline(
        pipeline_name="tmdb_raw_discover",
        destination="postgres",
        dataset_name="tmdb_data" 
    )

    source_data = tmdb_source(max_pages=2)
    load_info = pipeline.run(source_data)

    print("✅ Pipeline run finished!")
    print(load_info)