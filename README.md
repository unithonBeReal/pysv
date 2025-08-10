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

The server will start on `http://localhost:5000` by default.

### Environment Variables

The app loads environment variables from a `.env` file. You can customize the host and port by editing the `.env` file:

```bash
# Copy the example file
cp env.example .env

# Edit .env file
FLASK_HOST=127.0.0.1
FLASK_PORT=8000
```

You can also set environment variables directly:

```bash
# Set custom host and port
export FLASK_HOST=127.0.0.1
export FLASK_PORT=8000
python app.py

# Or run with inline environment variables
FLASK_HOST=127.0.0.1 FLASK_PORT=8000 python app.py
```

**Default values:**
- `FLASK_HOST`: `0.0.0.0` (all interfaces)
- `FLASK_PORT`: `5000`

## API Endpoints

- `GET /` - Basic hello world response
- `GET /api/hello` - API hello endpoint
- `GET /health` - Health check endpoint

## Example Usage

```bash
# Test the hello world endpoint
curl http://localhost:5000/

# Test the API hello endpoint
curl http://localhost:5000/api/hello

# Test the health check
curl http://localhost:5000/health
```

## Response Format

All endpoints return JSON responses with the following structure:
```json
{
  "message": "Hello, World!",
  "status": "success"
}
```
# pysv
