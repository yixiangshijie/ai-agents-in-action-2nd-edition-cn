# Image Generator API — Docker instructions

This project contains a FastAPI app at `02_app.py`.
The Dockerfile below builds a container that runs the app with Uvicorn.

Prerequisites
- Docker installed
- (Optional) `requirements.txt` in project root. If missing, the image will install minimal runtime deps.

Build (run from project root)
1. Open a terminal in the project root (where this Dockerfile is located).
2. Build the image:
   docker build -t image-generator:latest .

Run
- Basic:
  docker run --rm -p 8000:8000 -e OPENAI_API_KEY="your_key_here" image-generator:latest

- With a custom port:
  docker run --rm -p 9000:8000 -e OPENAI_API_KEY="your_key_here" -e PORT=8000 image-generator:latest

- Persist the container in Docker Desktop
  docker run --name image-gen -p 9000:8000 -e OPENAI_API_KEY="your_key_here" -e PORT=8000 image-generator:latest

Notes
- The app module used by Uvicorn is `02_app:app`. Ensure you run the container from the project root so Python can import.
- Provide any required environment variables (for example `OPENAI_API_KEY`) via `-e`.
- If the app depends on additional services (Chroma, MCP servers, etc.), start them separately and set any service URLs or paths as env vars before running the container.
- If you have a `requirements.txt` at project root, it will be installed during the image build. Otherwise minimal runtime deps are installed automatically.

Test the API
- Example curl to generate (replace key and payload as needed):
  curl -X POST "http://localhost:8000/generate" \
    -H "Content-Type: application/json" \
    -d '{"input":"A friendly robot teaching kids about solar energy"}' \
    --output image.png

Troubleshooting
- If imports fail, confirm the container built with your project's dependencies in `requirements.txt`.
- If the service hangs on first run (e.g., Chroma server initialization), re-run the container — initialization may take time on first startup.
- To iterate locally without rebuilding, mount the project into the container:
  docker run --rm -p 8000:8000 -v "$(pwd)":/app -e OPENAI_API_KEY="…" image-generator:latest

That's it — build the image from the project root and run with your API key set.
```// filepath: c:\Book_Code\AI-Agent-Workflows\README_DOCKER.md
# Image Generator API — Docker instructions

This project contains a FastAPI app at `chapter_08/02_app.py`.
The Dockerfile below builds a container that runs the app with Uvicorn.

Prerequisites
- Docker installed
- (Optional) `requirements.txt` in project root. If missing, the image will install minimal runtime deps.

Build (run from project root)
1. Open a terminal in the project root (where this Dockerfile is located).
2. Build the image:
   docker build -t image-generator:latest .

Run
- Basic:
  docker run --rm -p 8000:8000e OPENAI_API_KEY="your_key_here" image-generator:latest

- With a custom port:
  docker run --rm -p 9000:8000 -e OPENAI_API_KEY="your_key_here" -e PORT=8000 image-generator:latest

Notes
- The app module used by Uvicorn is `chapter_08.02_app:app`. Ensure you run the container from the project root so Python can import `chapter_08`.
- Provide any required environment variables (for example `OPENAI_API_KEY`) via `-e`.
- If the app depends on additional services (Chroma, MCP servers, etc.), start them separately and set any service URLs or paths as env vars before running the container.
- If you have a `requirements.txt` at project root, it will be installed during the image build. Otherwise minimal runtime deps are installed automatically.

Test the API
- Example curl to generate (replace key and payload as needed):
  curl -X POST "http://localhost:8000/generate" \
    -H "Content-Type: application/json" \
    -d '{"input":"A friendly robot teaching kids about solar energy"}' \
    --output image.png

Troubleshooting
- If imports fail, confirm the container built with your project's dependencies in `requirements.txt`.
- If the service hangs on first run (e.g., Chroma server initialization), re-run the container — initialization may take time on first startup.
- To iterate locally without rebuilding, mount the project into the container:
  docker run --rm -p 8000:8000 -v "$(pwd)":/app -e OPENAI_API_KEY="…" image-generator:latest

That's it — build the image from the project root and run with your API key set.