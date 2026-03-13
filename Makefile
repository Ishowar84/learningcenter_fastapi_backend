
.PHONY: run dev install clean format lint

# Default target
all: dev

# Run the backend with reload
dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run without reload
run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Install dependencies
install:
	uv sync

# Clean up temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Format code
format:
	uv run ruff format .

# Lints
lint:
	uv run ruff check .
