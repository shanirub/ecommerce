# Variables
COMPOSE_FILE=docker-compose.yml
ENV_FILE=local_settings.env

# Default target
.PHONY: run stop reset poetry-shell

run:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "Error: $(ENV_FILE) not found. Please create it first."; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "Docker container is running. You can now use the project."

stop:
	docker-compose -f $(COMPOSE_FILE) down
	@echo "Docker container stopped."

reset:
	docker-compose -f $(COMPOSE_FILE) down -v
	@echo "Docker container and volumes removed. Database reset complete."

poetry-shell:
	@if ! command -v poetry &> /dev/null; then \
		echo "Error: Poetry is not installed. Please install it first."; \
		exit 1; \
	fi
	poetry shell
	@echo "Poetry virtual environment activated."

help:
	@echo "Available commands:"
	@echo "  make run         Start the PostgreSQL container and environment."
	@echo "  make stop        Stop the running Docker container."
	@echo "  make reset       Stop and remove the Docker container and volumes."
	@echo "  make poetry-shell  Start the Poetry virtual environment."

