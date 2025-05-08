# Makefile for the GraphQL Filter Demo project

.PHONY: test run-server clean

# Default Python interpreter
PYTHON = python

# Activate virtual environment and run commands
# Assumes uv is used and the environment is .venv
# If a different venv name is used, update VENV_DIR
VENV_DIR = .venv
ACTIVATE_VENV = . $(VENV_DIR)/bin/activate &&

# Target to run tests
test:
	@echo "Running tests..."
	$(ACTIVATE_VENV) $(PYTHON) -m unittest discover -s tests -v

# Target to initialize DB, seed data, and run the server
run-server:
	@echo "Initializing database..."
	$(ACTIVATE_VENV) $(PYTHON) init_db.py
	@echo "Seeding data..."
	$(ACTIVATE_VENV) $(PYTHON) seed_data.py
	@echo "Starting server..."
	$(ACTIVATE_VENV) $(PYTHON) main.py

# Target to clean up (optional, can be expanded)
clean:
	@echo "Cleaning up..."
	@rm -f *.db
	@rm -rf $(VENV_DIR)
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
