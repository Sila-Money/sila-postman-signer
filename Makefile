# Convenience commands for running this local proxy signer.

# SHELL: Global Makefile setting.
# make will use /bin/bash instead of the default /bin/sh so that we can invoke source.
SHELL = /bin/bash

# VIRTUAL_ENV_DIR: name of the virtual env file to create in root directory.
VIRTUAL_ENV_DIR := env

# port: configurable local port on which to run this proxy server.
port ?= 8181

DOCKER_IMAGE := sila-signer-server
IMAGE_VERSION = $(shell grep "LABEL Version" Dockerfile | sed -e "s/.*=\"\(.*\)\"/\1/")

.PHONY := venv deps clean venv runserver docker-image docker-run

list:
	@printf "\n\tTARGETS: venv deps clean venv runserver docker-image docker-run\n\n"

# venv creates a virtual environment for containing versioned dependencies.
venv:
	@python3 -m venv $(VIRTUAL_ENV_DIR)
	@$(MAKE) deps --no-print-directory
	@echo "Your virtual environment has been created with all dependencies installed."

# deps installs dependencies to the virtual environment created with venv.
deps:
	@( \
		source ./$(VIRTUAL_ENV_DIR)/bin/activate; \
		pip3 install -r requirements.txt --use-feature=2020-resolver; \
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

docker-image:
	@docker build -t ${DOCKER_IMAGE}:${IMAGE_VERSION} .

docker-run:
	@docker run -p ${port}:${port} ${DOCKER_IMAGE}:${IMAGE_VERSION}
