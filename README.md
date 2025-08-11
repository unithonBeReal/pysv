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