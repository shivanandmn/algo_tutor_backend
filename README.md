# AlgoTutor Backend

A Python-based backend for the AlgoTutor application, using LiveKit for real-time communication.

## Project Structure

```
.
├── app/                      # Main application package
│   ├── agents/              # Agent implementations
│   │   └── base/            # Base agent functionality
├── .github/                 # GitHub configurations
│   └── workflows/           # GitHub Actions workflows
├── .env                     # Environment variables
├── .dockerignore           # Docker ignore file
├── Dockerfile              # Docker configuration
├── main.py                 # Application entry point
├── README.md              # Project documentation
└── requirements.txt       # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (for containerization)
- GCP account (for deployment)

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd algo_tutor_backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   python main.py start
   ```

### Docker Development

Build and run using Docker:

```bash
docker build -t algo-tutor-backend .
docker run -p 8080:8080 --env-file .env algo-tutor-backend
```

## Deployment

### Google Cloud Run

The application is configured for automatic deployment to Google Cloud Run using GitHub Actions.

1. Set up GitHub Secrets:
   - `GCP_SA_KEY`: GCP Service Account key (JSON)
   - `PROJECT_ID`: GCP Project ID
   - `REGION`: GCP Region (e.g., us-central1)
   - `SERVICE_NAME`: Cloud Run service name
   - `OPENAI_API_KEY`: OpenAI API key
   - `LIVEKIT_API_KEY`: LiveKit API key
   - `LIVEKIT_API_SECRET`: LiveKit API secret

2. Push to main branch to trigger deployment:
   ```bash
   git push origin main
   ```

3. Monitor deployment in GitHub Actions tab and Google Cloud Console

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `LIVEKIT_API_KEY`: Your LiveKit API key
- `LIVEKIT_API_SECRET`: Your LiveKit API secret
- `PORT`: Port for the application (default: 8080)