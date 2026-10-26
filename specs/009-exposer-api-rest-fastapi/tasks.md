---

description: "Task list for exposing the FastAPI HTTP REST API for n8n and WAHA"
---

# Tasks: Exposition du Service Web d'Intégration des Contacts Parents pour l'Automatisation et la Messagerie

**Input**: Design documents from `/specs/009-exposer-api-rest-fastapi/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/contrat-api-rest.md, quickstart.md

**Tests**: Inclus conformément aux critères d'acceptation de l'issue #5 et à la spécification (`tests/test_environment.py`, `tests/test_persistence.py` et `tests/test_api.py` avec `fastapi.testclient.TestClient`).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Package & API**: `sgdf_contacts/`, `sgdf_contacts/entrypoints/api.py`, `tests/`, `flake.nix`, `devbox.json`, `README.md` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Déclaration en parité stricte de `fastapi`, `uvicorn`, `python-multipart` et `httpx` dans `flake.nix` et `devbox.json`, mise à jour des tests d'environnement et création du sous-package `sgdf_contacts/entrypoints/`.

- [X] T001 [P] Ajouter `fastapi`, `uvicorn`, `python-multipart` et `httpx` dans `python3.withPackages` ainsi que dans le message `shellHook` de `flake.nix`
- [X] T002 [P] Ajouter `python3Packages.fastapi@latest`, `python3Packages.uvicorn@latest`, `python3Packages.python-multipart@latest` et `python3Packages.httpx@latest` en parité stricte (ainsi que dans `init_hook` et `check_environment`) dans `devbox.json`
- [X] T003 [P] Mettre à jour `REQUIRED_PYTHON_MODULES` (`fastapi`, `uvicorn`, `multipart`, `httpx`) et `EXPECTED_NIX_PACKAGES` (`fastapi`, `uvicorn`, `python-multipart`, `httpx`) dans `tests/test_environment.py`
- [X] T004 Créer le répertoire du sous-package `sgdf_contacts/entrypoints/` avec un fichier d'initialisation `sgdf_contacts/entrypoints/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Enrichissement du dépôt `ParentContactRepository` (accès aux enregistrements persistés `ParentRecord` avec leurs enfants ordonnés, normalisation téléphone compatible WAHA `@c.us`, mise à jour par `parent_id`, filtres sur les exports) et socle de l'application FastAPI (`ApiSettings`, schémas communs `ChildResponse`/`ParentResponse`, fabrique `create_app`).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Enrichir `ParentContactRepository` dans `sgdf_contacts/persistence/repository.py` avec les méthodes orientées `ParentRecord` + enfants ordonnés : `list_parent_records(self, *, short_unit: str | None = None, registration_status: str | None = None, has_valid_mobile: bool | None = None, include_inactive: bool = False) -> list[tuple[ParentRecord, list[AttachedChild]]]`, `get_parent_record_by_id(self, parent_id: int) -> tuple[ParentRecord, list[AttachedChild]] | None`, `update_parent_metadata(self, parent_id: int, *, has_whatsapp: bool | None) -> tuple[ParentRecord, list[AttachedChild]] | None`, `find_record_by_phone(self, phone: str, *, include_inactive: bool = False) -> tuple[ParentRecord, list[AttachedChild]] | None` (supportant `+336...`, `06...`, `336...` et `336...@c.us`), et prise en charge des filtres optionnels dans `export_vcf` et `export_excel`
- [X] T006 Implémenter `ApiSettings` (`SGDF_DATABASE_URL` défaut `"sqlite:///sgdf_contacts.db"`, `SGDF_API_KEY` défaut `None`, `SGDF_HOST` défaut `"127.0.0.1"`, `SGDF_PORT` défaut `8000`) et les schémas Pydantic de base `ChildResponse` (`first_name`, `last_name`, `full_name`, `short_unit`, `registration_status`) et `ParentResponse` (`id`, `member_id`, `last_name`, `first_name`, `full_name`, `primary_mobile_phone`, `secondary_mobile_phone`, `landline_phone`, `email_address`, `street`, `postal_code`, `city`, `notes`, `has_whatsapp: bool | None`, `is_active: bool`, `first_seen_at: datetime`, `updated_at: datetime`, `units: list[str]`, `children: list[ChildResponse]`) dans `sgdf_contacts/entrypoints/api.py`

**Checkpoint**: Le dépôt enrichi et les modèles de transfert de base sont prêts pour l'implémentation des User Stories.

---

## Phase 3: User Story 4 - Supervision de santé, documentation interactive et sécurisation par clé d'API (Priority: P1)

**Goal**: Permettre de superviser l'état du service et de la connexion SQLite via `GET /health` (sans authentification), d'accéder à la spécification OpenAPI sur `/docs` et `/openapi.json`, et de sécuriser toutes les routes `/api/v1/*` par l'en-tête `X-API-Key` dès que `SGDF_API_KEY` est définie.

**Independent Test**: Instancier `TestClient` sur `create_app`, vérifier que `/health`, `/docs` et `/openapi.json` répondent `200`, et vérifier que toute route `/api/v1/*` retourne `401` (clé absente) ou `403` (clé erronée) lorsque `SGDF_API_KEY` est configurée, et `200` lorsque la clé est valide ou non configurée.

### Implementation for User Story 4

- [X] T007 [US4] Implémenter la dépendance d'authentification `verify_api_key` (basée sur `APIKeyHeader(name="X-API-Key", auto_error=False)`, retournant `401` si absente et `403` si invalide lorsque `SGDF_API_KEY` est non vide), le schéma `HealthResponse` (`status: str`, `database: str`), l'endpoint public `GET /health` (exécutant `SELECT 1` sur SQLite) et la fabrique `create_app` + instance `app` dans `sgdf_contacts/entrypoints/api.py`
- [X] T008 [US4] Écrire les tests d'intégration de `GET /health`, `/docs`, `/openapi.json`, de la configuration `SGDF_*` et du contrôle d'accès `X-API-Key` (`401`, `403`, `200` avec et sans `SGDF_API_KEY`) dans `tests/test_api.py`

**Checkpoint**: Le serveur FastAPI, sa documentation OpenAPI, son endpoint `/health` et sa sécurité `X-API-Key` sont opérationnels et testés.

---

## Phase 4: User Story 1 - Import distant d'un export d'adhérents et obtention du rapport de différentiel (Priority: P1) 🎯 MVP

**Goal**: Téléverser un fichier `ExportIndividus.xls` en multipart sur `POST /api/v1/imports/intranet`, exécuter la synchronisation transactionnelle en base et retourner le rapport JSON complet (`total_parents`, `created`, `updated`, `unchanged`, `deactivated` et détail des changements).

**Independent Test**: Envoyer `ExportIndividus.xls` via `POST /api/v1/imports/intranet` sur une base vierge (`total_parents: 134`, `created: 134`), le renvoyer une seconde fois (`unchanged: 134`, `created: 0`, `updated: 0`), puis envoyer un export modifié et un fichier invalide (`400`) avec `TestClient`.

### Implementation for User Story 1

- [X] T009 [US1] Définir les schémas Pydantic `FieldChangeResponse` (`old_value`, `new_value`), `ParentSummaryResponse`, `ParentUpdateDiffResponse` (`parent`, `changes`), `ImportDiffDetailsResponse` (`created`, `updated`, `unchanged`, `deactivated`) et `ImportReportResponse` (`total_parents: int`, `created: int`, `updated: int`, `unchanged: int`, `deactivated: int`, `changes: ImportDiffDetailsResponse`) et implémenter `POST /api/v1/imports/intranet` (upload multipart `UploadFile`, gestion d'erreurs `400` en français sur fichier vide ou invalide) dans `sgdf_contacts/entrypoints/api.py`
- [X] T010 [US1] Ajouter les tests d'intégration de `POST /api/v1/imports/intranet` (premier import des 134 parents, second import idempotent, import avec modifications/désactivations détaillées et rejet `400` d'un fichier invalide) dans `tests/test_api.py`

**Checkpoint**: User Story 1 est fonctionnelle et testable indépendamment (MVP d'alimentation distante de la base via l'API).

---

## Phase 5: User Story 2 - Récupération des destinataires de messagerie par unité et identification d'un parent par numéro de téléphone (Priority: P1)

**Goal**: Exposer `GET /api/v1/units/{unit_name}/whatsapp-recipients` (retournant les parents actifs d'une unité ayant un mobile valide avec `waha_chat_id` au format `33687966975@c.us`, `phone_e164`, `first_name`, `last_name`, `children`), `GET /api/v1/parents/by-phone/{phone}` (compatible `+336...`, `06...`, `336...` et `336...@c.us`) et `PATCH /api/v1/parents/{parent_id}` (mise à jour partielle de `has_whatsapp`).

**Independent Test**: Sur une base alimentée, interroger `GET /api/v1/units/FARFADETS/whatsapp-recipients` (et avec code court `LJ`), rechercher un parent via `GET /api/v1/parents/by-phone/+336...`, `06...` et `336...@c.us`, puis modifier `has_whatsapp` via `PATCH /api/v1/parents/{parent_id}` et vérifier la persistance.

### Implementation for User Story 2

- [X] T011 [US2] Définir `WhatsAppRecipientResponse` (`parent_id: int`, `first_name: str`, `last_name: str`, `full_name: str`, `phone_e164: str`, `waha_chat_id: str`, `has_whatsapp: bool | None`, `children: list[ChildResponse]`) et `ParentPatchRequest` (`has_whatsapp: bool | None = None`), et implémenter les endpoints `GET /api/v1/units/{unit_name}/whatsapp-recipients`, `GET /api/v1/parents/by-phone/{phone}` et `PATCH /api/v1/parents/{parent_id}` dans `sgdf_contacts/entrypoints/api.py`
- [X] T012 [US2] Ajouter les tests d'intégration de `GET /api/v1/units/{unit_name}/whatsapp-recipients` (format `336...@c.us`, repli sur mobile secondaire, exclusion des parents sans mobile), de `GET /api/v1/parents/by-phone/{phone}` (`+336...`, `06...`, `336...`, `336...@c.us` et `404` si inconnu) et de `PATCH /api/v1/parents/{parent_id}` (`200` et `404`) dans `tests/test_api.py`

**Checkpoint**: L'intégration bidirectionnelle n8n / WAHA (diffusion par unité, identification d'expéditeur et mise à jour de `has_whatsapp`) est opérationnelle et testée.

---

## Phase 6: User Story 3 - Consultation filtrée des parents et téléchargement à la volée des fichiers de contacts (Priority: P2)

**Goal**: Exposer `GET /api/v1/parents` (liste filtrée et paginée avec `?unit=...`, `?has_mobile=...`, `?registration_status=...`, `?active_only=...`, `?limit=...`, `?offset=...`) ainsi que `GET /api/v1/exports/vcf` et `GET /api/v1/exports/xlsx` pour télécharger à la volée `ContactParents.vcf` et `ContactsParents.xlsx` depuis la base avec filtres optionnels.

**Independent Test**: Appeler `GET /api/v1/parents` avec différentes combinaisons de filtres et pagination, puis télécharger `/api/v1/exports/vcf` et `/api/v1/exports/xlsx` (sans filtre et avec `?unit=FARFADETS`) et vérifier les types MIME, les en-têtes `Content-Disposition` et le contenu des fichiers générés.

### Implementation for User Story 3

- [X] T013 [US3] Implémenter les endpoints `GET /api/v1/parents` (paramètres `unit`, `has_mobile`, `registration_status`, `active_only`, `limit`, `offset`), `GET /api/v1/exports/vcf` (`text/vcard; charset=utf-8`, `filename="ContactParents.vcf"`) et `GET /api/v1/exports/xlsx` (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `filename="ContactsParents.xlsx"`) dans `sgdf_contacts/entrypoints/api.py`
- [X] T014 [US3] Ajouter les tests d'intégration de `GET /api/v1/parents` (filtres combinés et pagination `limit`/`offset`) et de `GET /api/v1/exports/vcf` et `GET /api/v1/exports/xlsx` (sans filtre sur les 134 parents et avec filtres) dans `tests/test_api.py`

**Checkpoint**: Toutes les User Stories (US1, US2, US3, US4) sont complètes et vérifiées indépendamment.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Exposition publique dans `sgdf_contacts/entrypoints/__init__.py` et `sgdf_contacts/__init__.py`, mise à jour de `README.md` en français, validation complète `pytest` + `ruff`, commits avec messages en anglais et création de la Pull Request dédiée via `gh`.

- [X] T015 [P] Exporter `app`, `create_app` et `ApiSettings` dans `sgdf_contacts/entrypoints/__init__.py` et `sgdf_contacts/__init__.py`
- [X] T016 [P] Mettre à jour `README.md` en français pour documenter l'API HTTP REST FastAPI (`sgdf_contacts.entrypoints.api`), les variables d'environnement (`SGDF_DATABASE_URL`, `SGDF_API_KEY`, `SGDF_HOST`, `SGDF_PORT`), le démarrage avec `uvicorn` et les endpoints pour n8n et WAHA
- [X] T017 Exécuter la validation complète de bout en bout (`pytest` et `ruff check .`) dans l'environnement éphémère Nix conformément à `specs/009-exposer-api-rest-fastapi/quickstart.md`
- [X] T018 Enregistrer les modifications sur la branche `009-exposer-api-rest-fastapi` avec des messages de commit en anglais, pousser la branche vers `origin` et ouvrir une Pull Request dédiée via `gh pr create` (sans l'approuver ni la fusionner)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1 : T001–T004)**: Aucune dépendance — démarre immédiatement. T001, T002 et T003 sont parallélisables.
- **Foundational (Phase 2 : T005–T006)**: Dépend de la Phase 1 — bloque toutes les User Stories.
- **User Story 4 (Phase 3 : T007–T008)**: Dépend de la Phase 2 (fournit l'application `app`, `/health` et la sécurité `X-API-Key`).
- **User Story 1 (Phase 4 : T009–T010)**: Dépend de la Phase 3.
- **User Story 2 (Phase 5 : T011–T012)**: Dépend de la Phase 3.
- **User Story 3 (Phase 6 : T013–T014)**: Dépend de la Phase 3.
- **Polish (Phase 7 : T015–T018)**: Dépend de la complétion des Phases 3 à 6.

### User Story Dependencies

- **User Story 4 (P1)**: Socle HTTP, `/health`, OpenAPI et authentification `X-API-Key`.
- **User Story 1 (P1 - MVP)**: Import multipart `POST /api/v1/imports/intranet` et rapport de différentiel JSON.
- **User Story 2 (P1)**: Destinataires WAHA par unité, recherche par téléphone (`+336...`, `06...`, `336...@c.us`) et `PATCH /api/v1/parents/{parent_id}`.
- **User Story 3 (P2)**: Liste filtrée/paginée des parents et téléchargement à la volée `.vcf` / `.xlsx`.

### Parallel Opportunities

- En Phase 1 : `T001` (`flake.nix`), `T002` (`devbox.json`) et `T003` (`tests/test_environment.py`) portent sur des fichiers distincts et peuvent être exécutés en parallèle.
- En Phase 7 : `T015` (`__init__.py`) et `T016` (`README.md`) peuvent être exécutés en parallèle.

---

## Parallel Example: Setup Phase

```bash
# Exécution parallèle des mises à jour d'environnement Nix/Devbox et des tests associés :
Task T001: "Ajouter fastapi, uvicorn, python-multipart et httpx dans flake.nix"
Task T002: "Ajouter fastapi, uvicorn, python-multipart et httpx dans devbox.json"
Task T003: "Mettre à jour REQUIRED_PYTHON_MODULES et EXPECTED_NIX_PACKAGES dans tests/test_environment.py"
```

---

## Implementation Strategy

### MVP First (User Story 4 + User Story 1)

1. Compléter Phase 1 (Setup Nix/Devbox) et Phase 2 (Repository + modèles de base).
2. Compléter Phase 3 (User Story 4 : `/health`, `/docs`, `/openapi.json`, `X-API-Key`) et Phase 4 (User Story 1 : `POST /api/v1/imports/intranet`).
3. **STOP & VALIDATE** : Vérifier que le service démarre, protège `/api/v1/*` par `X-API-Key` et importe `ExportIndividus.xls` avec un rapport de différentiel exact.

### Incremental Delivery

1. Setup + Foundational → Environnement FastAPI/Uvicorn/HTTPX et méthodes de dépôt prêts.
2. User Story 4 + User Story 1 → Supervision `/health`, sécurité `X-API-Key` et import intranet opérationnels.
3. User Story 2 → Endpoints WAHA (`whatsapp-recipients`, `by-phone` multi-formats, `PATCH /parents/{id}`) opérationnels.
4. User Story 3 → Consultation filtrée `/api/v1/parents` et exports à la volée `/api/v1/exports/vcf` et `/api/v1/exports/xlsx` opérationnels.
5. Polish → Mise à jour de `README.md`, validation complète `pytest` + `ruff`, commits en anglais et ouverture de la Pull Request dédiée via `gh`.
