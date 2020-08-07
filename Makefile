# Convenience commands for running this local proxy signer.

# SHELL: Global Makefile setting.
# make will use /bin/bash instead of the default /bin/sh so that we can invoke source.
SHELL = /bin/bash

# VIRTUAL_ENV_DIR: name of the virtual env file to create in root directory.
VIRTUAL_ENV_DIR := env

# port: configurable local port on which to run this proxy server.
port ?= 8181

# venv creates a virtual environment for containing versioned dependencies.
venv:
	@python3 -m venv $(VIRTUAL_ENV_DIR)
	@$(MAKE) deps --no-print-directory
	@echo "Your virtual environment has been created with all dependencies installed."

# deps installs dependencies to the virtual environment created with venv.
deps:
	@( \
		source ./$(VIRTUAL_ENV_DIR)/bin/activate; \
		pip3 install -r requirements.txt; \
	)

# clean removes __pycache__ folders.
clean:
	@find . -type d -name __pycache__ -exec rm -rf {} \+

# venvclean removes the virtual environment directory.
venvclean:
	@rm -rf $(VIRTUAL_ENV_DIR)

# runserver runs a local (debug-mode) server on the configured port.
runserver:
	@( \
		source ./$(VIRTUAL_ENV_DIR)/bin/activate; \
		export FLASK_APP=signerserver/application.py; \
		export FLASK_ENV=production; \
		flask run --port=$(port); \
	)
