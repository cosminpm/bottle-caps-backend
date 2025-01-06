# Define the FastAPI app module and command
UVICORN_COMMAND :=

# Run the FastAPI app using uvicorn locally
run-local:
	@uvicorn app.main:app --use-colors

run:
	@uvicorn app.main:app --use-colors --host 0.0.0.0 --port 8080

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


# Update the env files
env-update:
	scp .env root@<IP_ADDRESS>:/root/app/bottle-caps-backend
