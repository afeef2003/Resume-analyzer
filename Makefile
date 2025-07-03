.PHONY: install run test clean docker-build docker-run

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	python run_tests.py

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f checkpoints.db

# Docker commands
docker-build:
	docker build -t resume-analyzer .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

# Development setup
dev-setup:
	cp .env.example .env
	echo "Please edit .env file with your OpenAI API key"

# Full setup for new users
setup: dev-setup install
	echo "Setup complete! Edit .env file and run 'make run'"