# venv created with 'uv venv --python /Users/sanjaykapoor/.pyenv/shims/python3.12'
VENV = .venv
PIP = pip
PYTHON = $(VENV)/bin/python3
SHELL = /bin/bash

.PHONY: build clean console dev deploy install prd test

build:
	./scripts/docker-utils build

console:
	python

dev: 
	. $(VENV)/bin/activate && ./bin/app-server --port 9119

install: pyproject.toml
	uv sync

prd:
	. $(VENV)/bin/activate && ./bin/app-server --port 9119

test:
	. $(VENV)/bin/activate && pytest

clean:
	rm -rf __pycache__
	rm -rf $(VENV)
