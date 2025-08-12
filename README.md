# Flask API Server

A basic Flask backend API server with hello world endpoints.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Copy the example environment file
cp env.example .env

# Edit .env file with your desired values
# FLASK_HOST=0.0.0.0
# FLASK_PORT=5000
```

3. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:8000` by default.

## Docker Production Setup

### Building and Running with Docker

1. Build the Docker image:
```bash
docker build -t pysv .
```

2. Run the container:
```bash
docker run -d \
  --name pysv-app \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e GEMINI_API_KEY=your_api_key_here \
  pysv
```

### Using Docker Compose (Recommended)

1. Create a `.env` file with your environment variables:
```bash
cp env.example .env
# Edit .env file with your values, especially GEMINI_API_KEY
```

2. Run with Docker Compose:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. Check logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

4. Stop the service:
```bash
docker-compose -f docker-compose.prod.yml down
```

The application will be available at `http://localhost:8000`.

### Environment Variables

The app loads environment variables from a `.env` file. You can customize the host and port by editing the `.env` file:

```bash
# Copy the example file
cp env.example .env

# Edit .env file
FLASK_HOST=127.0.0.1
FLASK_PORT=8000
DATA_PATH=./data
CONFIG_FILE_PATH=./data/config.json
```

### Configs

`./data/config.json`


```
{
  "dee_token": "",
  "dee_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}
```

### Service Key

`./google-service-key.json`

## API

- GET /api/tasks
- POST /api/tasks
- GET /api/tasks/<task_id>/result
- GET /api/tasks/<task_id>/thumbnail