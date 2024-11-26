# Define the default target
.DEFAULT_GOAL := run

# Define the FastAPI app module and command
APP_MODULE := app.main:app
UVICORN_COMMAND := uvicorn $(APP_MODULE) --use-colors

# Run the FastAPI app using uvicorn
run:
	@$(UVICORN_COMMAND)

generate:
	@python -m scripts.generate_model

# Install dependencies from the requirements file
install:
	@pip install -r requirements.txt
	@pip install -r requirements-other.txt

# Uninstall all currently installed packages
uninstall:
	@pip freeze | xargs pip uninstall -y

# Powershell:
# pip freeze | ForEach-Object { pip uninstall -y $_ }


# Format code according to predefined style rules
format:
	@ruff format .
	@ruff check . --fix
	@mypy --config-file "pyproject.toml"



