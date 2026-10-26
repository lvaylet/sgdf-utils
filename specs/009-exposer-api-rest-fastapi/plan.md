# Implementation Plan: Exposition du Service Web d'Intégration des Contacts Parents pour l'Automatisation et la Messagerie

**Branch**: `009-exposer-api-rest-fastapi` | **Date**: 2026-10-26 | **Spec**: [specs/009-exposer-api-rest-fastapi/spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-exposer-api-rest-fastapi/spec.md`

## Summary

Exposer les fonctionnalités du package `sgdf_contacts` et de sa couche de persistance SQLite (`sgdf_contacts.persistence`) via une **API HTTP REST (`FastAPI`)** dotée d'une spécification OpenAPI automatique (`/docs`, `/openapi.json`), conçue pour être appelée par **n8n** et **WAHA** sur le homelab domestique :
1. Déclarer `fastapi`, `uvicorn`, `python-multipart` et `httpx` en parité stricte dans `flake.nix` et `devbox.json`, et mettre à jour `tests/test_environment.py`.
2. Étendre `ParentContactRepository` (`sgdf_contacts/persistence/repository.py`) avec les méthodes orientées enregistrement persistant (`ParentRecord` + enfants ordonnés) nécessaires à l'API (`list_parent_records`, `find_record_by_phone` prenant en charge `+336...`, `06...`, `336...` et `336...@c.us`, `get_parent_record_by_id`, `update_parent_metadata`) ainsi que le filtrage optionnel sur `export_vcf` et `export_excel`.
3. Créer le sous-package `sgdf_contacts/entrypoints/` (`sgdf_contacts/entrypoints/api.py` et `__init__.py`) exposant l'application FastAPI (`app` et fabrique `create_app`), la configuration par variables d'environnement (`SGDF_DATABASE_URL`, `SGDF_API_KEY`, `SGDF_HOST`, `SGDF_PORT`), la sécurité par en-tête `X-API-Key` sur `/api/v1/*`, et les 8 endpoints requis (`GET /health`, `POST /api/v1/imports/intranet`, `GET /api/v1/parents`, `GET /api/v1/units/{unit_name}/whatsapp-recipients`, `GET /api/v1/parents/by-phone/{phone}`, `PATCH /api/v1/parents/{parent_id}`, `GET /api/v1/exports/vcf`, `GET /api/v1/exports/xlsx`).

## Technical Context

**Language/Version**: Python 3.14 (fourni par l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv`)

**Primary Dependencies**: `fastapi`, `uvicorn`, `python-multipart`, `httpx`, `sqlmodel`, `sqlalchemy`, `beautifulsoup4`, `lxml`, `openpyxl`, bibliothèque standard Python (`dataclasses`, `datetime`, `io`, `os`, `pathlib`, `typing`), `pytest` et `ruff`

**Storage**: Base SQLite locale (en mode WAL avec `foreign_keys=ON`, configurée via `SGDF_DATABASE_URL`, par défaut `sqlite:///sgdf_contacts.db`) + téléversement en mémoire (`ExportIndividus.xls`) et génération à la volée (`ContactParents.vcf`, `ContactsParents.xlsx`)

**Testing**: `pytest` avec `fastapi.testclient.TestClient` (`tests/test_api.py` couvrant tous les endpoints, l'authentification `X-API-Key`, les formats WAHA `336...@c.us` et l'idempotence d'import) et `ruff check .`

**Target Platform**: Environnement éphémère Linux / macOS activé par `direnv` / Homelab domestique (n8n + WAHA)

**Project Type**: Package Python modulaire (`sgdf_contacts/`) + API HTTP REST FastAPI (`sgdf_contacts/entrypoints/api.py`) + scripts CLI Python 3

**Performance Goals**: Import multipart complet de `ExportIndividus.xls` (134 parents) et calcul de différentiel en moins de 1 seconde ; requêtes de lecture et recherche par téléphone en moins de 50 ms

**Constraints**: Identifiants de code en anglais et commentaires, docstrings, messages d'erreur HTTP et documentation (`README.md`) en français (Principe I, constitution v2.1.0) ; déclaration des dépendances dans `flake.nix` et `devbox.json` en parité stricte (Principe II) ; protection des données personnelles avec authentification `X-API-Key` et aucune donnée nominative en dur (Principe IV) ; simplicité et réutilisation directe de `ParentContactRepository` sans surcouche inutile (Principe V — YAGNI) ; travail sur branche dédiée `009-exposer-api-rest-fastapi`, messages de commit en anglais (consigne utilisateur) et ouverture d'une Pull Request dédiée via `gh` sans auto-fusion (Principe VI)

**Scale/Scope**: 134 parents uniques et leurs enfants rattachés dans `ExportIndividus.xls`, 8 endpoints HTTP REST documentés en OpenAPI, intégration directe avec n8n et WAHA

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution (v2.1.0) | Statut | Justification de conformité |
| -------------------------------------- | -------- | ----------------------------- |
| **I. Code en Anglais et Documentation en Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Tous les identifiants Python (`entrypoints`, `api.py`, `create_app`, `ApiSettings`, `verify_api_key`, schémas Pydantic, routes et fonctions) sont en anglais (PEP 8). Les commentaires, docstrings, descriptions OpenAPI, messages d'erreur HTTP et la documentation `README.md` sont en français. (Note : les messages de commit Git seront rédigés en anglais conformément à la demande explicite de l'utilisateur dans le prompt). |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | `fastapi`, `uvicorn`, `python-multipart` et `httpx` sont déclarés en parité stricte dans `flake.nix` et `devbox.json`, et vérifiés automatiquement dans `tests/test_environment.py`. |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Le point d'entrée `sgdf_contacts/entrypoints/api.py` réutilise le domaine, les parseurs, les exporteurs et le dépôt SQLite existants, et peut être lancé directement via `uvicorn sgdf_contacts.entrypoints.api:app` ou `python3 -m sgdf_contacts.entrypoints.api`. |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | Aucune donnée personnelle n'est codée en dur ; l'authentification `X-API-Key` protège toutes les routes `/api/v1/*` dès que `SGDF_API_KEY` est définie ; l'upload `ExportIndividus.xls` est traité en mémoire sans altérer le fichier source. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | Architecture FastAPI claire et concise concentrée dans `sgdf_contacts/entrypoints/api.py` s'appuyant directement sur `ParentContactRepository` et `SQLModel`. |
| **VI. Flux Git par Branche Dédiée et Pull Request (Squash and Merge)** | ✅ CONFORME | Développement réalisé sur la branche dédiée `009-exposer-api-rest-fastapi` et création d'une Pull Request dédiée via `gh pr create` sans approbation ni fusion automatique. |

## Project Structure

### Documentation (this feature)

```text
specs/009-exposer-api-rest-fastapi/
├── plan.md                                  # Ce fichier (/speckit.plan)
├── research.md                              # Décisions techniques Phase 0
├── data-model.md                            # Schémas de requête/réponse API et règles métier Phase 1
├── quickstart.md                            # Guide de validation de bout en bout Phase 1
├── contracts/                               # Contrats d'interface Phase 1
│   └── contrat-api-rest.md                  # Contrat détaillé des endpoints HTTP REST et de l'authentification
└── tasks.md                                 # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
flake.nix                                    # Ajout de fastapi, uvicorn, python-multipart et httpx dans python3.withPackages
devbox.json                                  # Ajout de fastapi, uvicorn, python-multipart et httpx en parité stricte
sgdf_contacts/
├── __init__.py                              # Ré-export de create_app / app depuis entrypoints
├── domain/                                  # Inchangé (zéro dépendance externe)
├── parsers/                                 # Inchangé
├── exporters/                               # Inchangé
├── persistence/
│   ├── __init__.py                          # Export public mis à jour si nécessaire
│   ├── models.py                            # Inchangé
│   └── repository.py                        # Enrichi avec requêtage orienté ParentRecord (id, has_whatsapp, timestamps), normalisation téléphone WAHA (@c.us) et filtres sur export_vcf / export_excel
└── entrypoints/
    ├── __init__.py                          # Export public de app et create_app
    └── api.py                               # Application FastAPI, configuration env (SGDF_*), sécurité X-API-Key, schémas Pydantic et routes HTTP
README.md                                    # Documentation mise à jour en français (lancement de l'API, variables d'environnement, endpoints n8n/WAHA)
tests/
├── test_environment.py                      # Mis à jour avec fastapi, uvicorn, multipart, httpx
├── test_extract_parent_contacts.py          # Conservé
├── test_generate_contacts_vcf.py            # Conservé
├── test_sgdf_contacts_package.py            # Conservé
├── test_persistence.py                      # Conservé / enrichi
└── test_api.py                              # Nouveau : tests d'intégration FastAPI avec TestClient (health, auth X-API-Key, import multipart, filtres parents, whatsapp-recipients WAHA, by-phone, patch parent, exports VCF/XLSX)
```

**Structure Decision**: Création du sous-package `sgdf_contacts/entrypoints/` contenant `api.py` conformément à l'architecture cible décrite dans l'issue #5 (`sgdf_contacts/entrypoints/api.py`), enrichissement léger de `ParentContactRepository` pour exposer les métadonnées de persistance (`id`, `has_whatsapp`, `is_active`, `first_seen_at`, `updated_at`), et ajout de la suite de tests `tests/test_api.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution.
