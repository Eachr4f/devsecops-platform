.RECIPEPREFIX := >
.DEFAULT_GOAL := help

API_DIR := services/api
VENV := $(API_DIR)/.venv

.PHONY: help install up down restart ps logs lint format test check secrets

help:
>@echo "make install  : préparer l'environnement Python"
>@echo "make up       : construire et démarrer l'application"
>@echo "make down     : arrêter sans supprimer les données"
>@echo "make restart  : redémarrer les services"
>@echo "make ps       : afficher l'état des services"
>@echo "make logs     : suivre les journaux"
>@echo "make lint     : vérifier le code et son formatage"
>@echo "make format   : appliquer le formatage"
>@echo "make test     : exécuter les tests avec couverture"
>@echo "make check    : exécuter lint et tests"
>@echo "make secrets  : analyser l'historique Git"
>@echo "make staged   : contrôler les fichiers préparés"
>@echo "make sast     : analyser le code avec Semgrep"
>@echo "make ci       : lancer lint, tests, Gitleaks, Semgrep et Trivy"
>@echo "make hooks    : activer le hook pre-commit"
>@echo "make scan     : analyser les dépendances, Dockerfiles et images avec Trivy"

install:
>python3 -m venv $(VENV)
>$(VENV)/bin/python -m pip install -r $(API_DIR)/requirements-dev.txt

up:
>docker compose up --build -d --wait --wait-timeout 120

down:
>docker compose down

restart:
>docker compose restart

ps:
>docker compose ps

logs:
>docker compose logs -f

lint:
>cd $(API_DIR) && .venv/bin/ruff check .
>cd $(API_DIR) && .venv/bin/ruff format --check .

format:
>cd $(API_DIR) && .venv/bin/ruff format .

test:
>cd $(API_DIR) && .venv/bin/python -m pytest -q --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=70

check: lint test

SEMGREP ?= $(HOME)/.local/share/devsecops-tools/semgrep/bin/semgrep

.PHONY: staged sast ci hooks scan

secrets:
>gitleaks git --no-banner --redact --log-opts="HEAD" .

staged:
>.githooks/pre-commit

sast:
>"$(SEMGREP)" scan --config p/default --config p/python --config p/flask --config p/dockerfile --metrics=off --error --severity ERROR .

scan:
>trivy fs --scanners vuln,misconfig --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 --skip-dirs "$(VENV)" .
>docker build --pull -t devsecops-api:ci services/api
>docker build --pull -t devsecops-frontend:ci services/frontend
>trivy image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 devsecops-api:ci
>trivy image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 devsecops-frontend:ci

ci:
>$(MAKE) lint
>$(MAKE) test
>$(MAKE) secrets
>$(MAKE) sast
>$(MAKE) scan

hooks:
>git config core.hooksPath .githooks
