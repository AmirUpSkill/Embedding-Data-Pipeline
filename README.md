# 🎬 TMDB Movie Data Pipeline

A professional Extract-Load-Transform (ELT) data pipeline that fetches movie data from The Movie Database (TMDB) API and stores it in PostgreSQL using DLT (Data Load Tool).

## 🌟 Features

- **🔄 Automated Data Extraction**: Fetches high-quality movie data from TMDB API
- **🐳 Fully Dockerized**: Complete development environment with Docker Compose
- **📊 Professional ELT**: Built with DLT framework for scalable data operations
- **🔒 Secure Configuration**: Proper secrets management with environment separation
- **⚡ Production Ready**: Containerized pipeline ready for deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TMDB API      │───▶│  DLT Pipeline   │───▶│  PostgreSQL     │
│   (Source)      │    │  (Transform)    │    │  (Destination)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Tech Stack
- **Pipeline Framework**: DLT (Data Load Tool)
- **Database**: PostgreSQL with pgvector extension
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.12
- **API**: The Movie Database (TMDB) v3

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- TMDB API Read Access Token ([Get one here](https://www.themoviedb.org/settings/api))
- Google Gemini API key (optional, for future AI features)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/tmdb-movie-pipeline.git
cd tmdb-movie-pipeline
```

### 2. Configure Secrets
Copy the example secrets file and add your API keys:
```bash
cp .dlt/secrets.toml.example .dlt/secrets.toml
```

Edit `.dlt/secrets.toml` with your credentials:
```toml
[destination.postgres.credentials]
database = "cinemax_db"
username = "postgres"
password = "password"
host = "db"
port = 5432

[sources.movie_pipeline.tmdb_discover]
api_token = "your_tmdb_api_token_here"

[sources.tmdb_pipeline.gemini]
api_key = "your_google_gemini_api_key_here"
```

### 3. Start the Environment
```bash
docker-compose up --build -d
```

### 4. Run the Pipeline
```bash
docker-compose exec pipeline python movie_pipeline.py
```

### 5. Verify Data
```bash
# Connect to database
docker-compose exec db psql -U postgres -d cinemax_db

# Check loaded data
SELECT COUNT(*) FROM tmdb_data.raw_movies;
SELECT title, release_date, vote_average FROM tmdb_data.raw_movies LIMIT 5;
```

## 📁 Project Structure

```
├── .dlt/                     # DLT configuration directory
│   ├── config.toml          # DLT pipeline configuration
│   └── secrets.toml         # API keys and database credentials (gitignored)
├── .venv/                   # Python virtual environment (gitignored)
├── postgres-data/           # PostgreSQL data volume (gitignored)
├── .env                     # Environment variables (gitignored)
├── .gitignore              # Git ignore patterns
├── docker-compose.yml       # Docker services definition
├── Dockerfile              # Python pipeline container definition
├── main.py                 # Standalone TMDB API test script
├── movie_pipeline.py       # Main DLT pipeline script
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🔧 Configuration

### Pipeline Configuration
The pipeline is configured through DLT's configuration system:

- **Pipeline Name**: `tmdb_raw_discover`
- **Dataset Name**: `tmdb_data` (PostgreSQL schema)
- **Destination**: PostgreSQL with pgvector
- **Write Disposition**: Merge (upsert based on movie ID)

### Data Schema
Movies are stored in the `tmdb_data.raw_movies` table with the following key fields:
- `id` (Primary Key)
- `title`
- `overview`
- `release_date`
- `vote_average`
- `vote_count`
- `poster_path`
- `genre_ids` (stored in separate table)

## 🔄 Pipeline Workflow

1. **Extract**: Fetch movie data from TMDB `/discover/movie` endpoint
2. **Transform**: DLT automatically handles schema inference and data types
3. **Load**: Insert/update data in PostgreSQL with automatic schema creation
4. **Validate**: Pipeline includes data quality checks and error handling

## 🐳 Docker Services

### Database Service (`db`)
- **Image**: `ankane/pgvector:latest`
- **Port**: `5432`
- **Features**: PostgreSQL with pgvector extension for future AI features

### Pipeline Service (`pipeline`)
- **Build**: Custom Python 3.12 slim container
- **Features**: DLT framework, TMDB API client, PostgreSQL adapter
- **Command**: Idle container for on-demand pipeline execution

## 🔐 Security Best Practices

- ✅ Secrets stored in `.dlt/secrets.toml` (gitignored)
- ✅ Environment variables for sensitive data
- ✅ No hardcoded credentials in source code
- ✅ Database password configurable via environment
- ✅ API tokens injected securely via DLT's secret management

## 📊 Data Quality

The pipeline implements several data quality measures:
- **Vote Count Filter**: Only movies with 200+ votes (ensures quality)
- **Sort by Rating**: Fetches highest-rated movies first
- **Primary Key Constraints**: Prevents duplicate movie entries
- **Schema Validation**: DLT automatically validates data types

## 🚀 Production Deployment

For production deployment:

1. **Environment Secrets**: Use proper secret management (AWS Secrets Manager, etc.)
2. **Database**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
3. **Scheduling**: Implement with Airflow, Prefect, or similar
4. **Monitoring**: Add logging, metrics, and alerting
5. **Scaling**: Consider distributed execution for large datasets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [TMDB](https://www.themoviedb.org/) for providing the movie data API
- [DLT](https://dlthub.com/) for the excellent ELT framework
- [PostgreSQL](https://www.postgresql.org/) for the robust database platform

## 📧 Support

For questions and support:
- Create an issue on GitHub
- Check the [DLT documentation](https://dlthub.com/docs)
- Review [TMDB API documentation](https://developers.themoviedb.org/3)

---
**Built with ❤️ using DLT, PostgreSQL, and Docker**
