# Quickstart Validation Guide: API HTTP REST (`FastAPI`) pour n8n et WAHA

**Feature**: `009-exposer-api-rest-fastapi` | **Date**: 2026-10-26

## Prérequis

1. Disposer de l'environnement éphémère Nix (`flake.nix`) ou Devbox (`devbox.json`) activé via `direnv`.
2. Vérifier que `fastapi`, `uvicorn`, `multipart` (`python-multipart`) et `httpx` sont disponibles dans l'environnement :

```bash
nix develop --command python3 -c "import fastapi, uvicorn, multipart, httpx; print('FastAPI:', fastapi.__version__)"
```

## Scénario 1 : Exécution des tests automatisés de l'API avec `TestClient`

Lancer la suite de tests dédiée à l'API (`tests/test_api.py`) qui valide l'ensemble des endpoints (`GET /health`, `/docs`, `/openapi.json`, authentification `X-API-Key`, import multipart `ExportIndividus.xls`, filtrage des parents, destinataires WAHA par unité, recherche par téléphone `+336...` / `06...` / `336...@c.us`, `PATCH /api/v1/parents/{parent_id}` et exports à la volée `.vcf` / `.xlsx`) :

```bash
nix develop --command pytest tests/test_api.py
```

**Résultat attendu** :
- 100 % des tests de `tests/test_api.py` passent avec succès.

## Scénario 2 : Démarrage du serveur avec `uvicorn` et vérification OpenAPI

Vérifier que l'application démarre et expose `/health` ainsi que `/openapi.json` :

```bash
nix develop --command python3 -c "
from fastapi.testclient import TestClient
from sgdf_contacts.entrypoints.api import create_app

app = create_app(database_url='sqlite:///:memory:', api_key='secret-test-key')
client = TestClient(app)

assert client.get('/health').status_code == 200
assert client.get('/openapi.json').status_code == 200
assert client.get('/api/v1/parents').status_code == 401
assert client.get('/api/v1/parents', headers={'X-API-Key': 'wrong'}).status_code == 403
assert client.get('/api/v1/parents', headers={'X-API-Key': 'secret-test-key'}).status_code == 200
print('Validation OpenAPI, Health et X-API-Key réussie.')
"
```

## Scénario 3 : Suite complète de tests et contrôle de qualité `ruff`

Exécuter l'intégralité des tests du dépôt et le linter `ruff` :

```bash
nix develop --command pytest
nix develop --command ruff check .
```

**Résultat attendu** :
- 100 % des suites de tests (`test_environment.py`, `test_extract_parent_contacts.py`, `test_generate_contacts_vcf.py`, `test_sgdf_contacts_package.py`, `test_persistence.py`, `test_api.py`) réussissent.
- `ruff check .` retourne `All checks passed!`.
