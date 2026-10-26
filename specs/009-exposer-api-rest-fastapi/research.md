# Research: Exposition de l'API HTTP REST (`FastAPI`) pour n8n et WAHA

**Feature**: `009-exposer-api-rest-fastapi` | **Date**: 2026-10-26

## Decision 1: Déclaration des dépendances Web et HTTP dans `flake.nix` et `devbox.json`

- **Decision**: Ajouter `fastapi`, `uvicorn`, `python-multipart` et `httpx` dans `flake.nix` (`python3.withPackages`) et dans `devbox.json` (`python3Packages.fastapi@latest`, `python3Packages.uvicorn@latest`, `python3Packages.python-multipart@latest`, `python3Packages.httpx@latest`), et mettre à jour les listes `REQUIRED_PYTHON_MODULES` (avec `fastapi`, `uvicorn`, `multipart`, `httpx`) et `EXPECTED_NIX_PACKAGES` dans `tests/test_environment.py`.
- **Rationale**:
  - `fastapi` fournit le routeur HTTP REST, la validation Pydantic/SQLModel et la génération automatique du schéma OpenAPI (`/docs`, `/openapi.json`).
  - `uvicorn` est le serveur ASGI standard pour exécuter l'application FastAPI en développement et en production sur le homelab.
  - `python-multipart` (importé sous le nom de module `multipart` / `python_multipart`) est requis par FastAPI/Starlette pour analyser les téléversements `multipart/form-data` (`UploadFile`) sur `POST /api/v1/imports/intranet`.
  - `httpx` est requis par `starlette.testclient.TestClient` / `fastapi.testclient.TestClient` pour exécuter les tests d'intégration dans `pytest`.
- **Alternatives considered**:
  - *Utiliser uniquement la bibliothèque standard (`http.server`)* : Écarté car l'issue #5 exige explicitement FastAPI, OpenAPI automatique et `TestClient`.

## Decision 2: Fabrique d'application (`create_app`) et configuration par variables d'environnement

- **Decision**: Structurer `sgdf_contacts/entrypoints/api.py` autour d'un objet de configuration `ApiSettings` (lisant dynamiquement `SGDF_DATABASE_URL`, `SGDF_API_KEY`, `SGDF_HOST`, `SGDF_PORT` depuis `os.environ`), d'une fabrique `create_app(database_url: str | Path | None = None, api_key: str | None = None) -> FastAPI` et d'une instance globale `app = create_app()` prête pour `uvicorn sgdf_contacts.entrypoints.api:app`.
- **Rationale**:
  - En lisant `SGDF_API_KEY` et `SGDF_DATABASE_URL` dynamiquement (ou via `app.state` initialisé par `create_app` avec repli sur `os.environ`), on permet à la fois une utilisation directe avec `uvicorn` en production et une isolation totale entre les tests `pytest` (utilisation de `monkeypatch.setenv` ou d'une base SQLite temporaire par test sans effet de bord).
  - Permet également d'exécuter `python3 -m sgdf_contacts.entrypoints.api` qui lance `uvicorn.run(app, host=settings.host, port=settings.port)`.
- **Alternatives considered**:
  - *Figer les variables d'environnement uniquement au moment de l'import du module* : Rendrait les tests d'authentification (`SGDF_API_KEY` activée/désactivée) et le changement de base de données plus fragiles dans `pytest`.

## Decision 3: Mécanisme d'authentification `X-API-Key` sur `/api/v1/*`

- **Decision**: Utiliser une dépendance de sécurité FastAPI basée sur `APIKeyHeader(name="X-API-Key", auto_error=False)` attachée au routeur `APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])`, tandis que `GET /health`, `/docs` et `/openapi.json` sont rattachés à l'application racine sans cette dépendance.
- **Rationale**:
  - Lorsque la clé configurée (`SGDF_API_KEY`) est vide ou absente, la dépendance `verify_api_key` laisse passer toutes les requêtes sans exiger l'en-tête.
  - Lorsqu'une clé `SGDF_API_KEY` non vide est configurée :
    - Si l'en-tête `X-API-Key` est manquant ou vide, la dépendance lève `HTTPException(status_code=401, detail="Clé d'API manquante dans l'en-tête X-API-Key.")`.
    - Si l'en-tête `X-API-Key` est présent mais ne correspond pas (comparaison en temps constant via `secrets.compare_digest`), la dépendance lève `HTTPException(status_code=403, detail="Clé d'API invalide.")`.
  - Intégrer `APIKeyHeader` au niveau du routeur `/api/v1` documente automatiquement le schéma de sécurité `X-API-Key` dans `/openapi.json` et le bouton *Authorize* dans `/docs`.
- **Alternatives considered**:
  - *Middleware HTTP global* : Nécessiterait de maintenir manuellement une liste d'exclusion pour `/health`, `/docs`, `/redoc`, `/openapi.json` et n'enrichirait pas automatiquement la spécification OpenAPI avec le schéma de sécurité.

## Decision 4: Normalisation WAHA (`waha_chat_id` et recherche `by-phone` multi-formats)

- **Decision**:
  1. **Formatage de `waha_chat_id` et `phone_e164` pour `GET /api/v1/units/{unit_name}/whatsapp-recipients`** :
     - Sélectionner le premier numéro mobile valide du parent : `primary_mobile_phone` si `is_valid_mobile_phone(primary_mobile_phone)` est vrai, sinon `secondary_mobile_phone` si `is_valid_mobile_phone(secondary_mobile_phone)` est vrai.
     - Ce numéro étant déjà normalisé au format E.164 (ex. `+33687966975`), `phone_e164` vaut `+33687966975` et `waha_chat_id` vaut `f"{phone_e164.lstrip('+')}@c.us"` (soit `33687966975@c.us`).
  2. **Recherche multi-formats sur `GET /api/v1/parents/by-phone/{phone}`** :
     - Avant d'appeler la normalisation téléphonique, retirer tout suffixe d'identifiant WhatsApp/WAHA (`@c.us`, `@s.whatsapp.net`, `@g.us`) ainsi que les espaces.
     - Si la chaîne nettoyée est composée de chiffres et commence par `33` (avec une longueur de 11 chiffres, ex. `33687966975`), la préfixer par `+` (`+33687966975`) avant d'appliquer `normalize_phone`.
     - Ainsi, `+33687966975`, `0687966975`, `06 87 96 69 75`, `33687966975` et `33687966975@c.us` convergent tous vers le même numéro normalisé `+33687966975` et retrouvent la fiche du parent sur `primary_mobile_phone`, `secondary_mobile_phone` ou `landline_phone`.
- **Rationale**:
  - Répond exactement au critère d'acceptation de l'issue #5 : *"Les formats retournés pour WAHA (`waha_chat_id`) et la recherche par téléphone acceptent aussi bien `+336...` que `336...@c.us`"*.
- **Alternatives considered**:
  - *Stocker `waha_chat_id` en base de données* : Redondant avec `primary_mobile_phone` / `secondary_mobile_phone` déjà normalisés en E.164 ; le calculer de façon déterministe évite toute désynchronisation.

## Decision 5: Structure du rapport JSON de `POST /api/v1/imports/intranet`

- **Decision**: Retourner un objet JSON structuré `ImportReportResponse` contenant :
  - `total_parents: int` (nombre total de parents actifs présents dans l'export importé : `len(created) + len(updated) + len(unchanged)`),
  - `created: int` (nombre de parents créés),
  - `updated: int` (nombre de parents mis à jour),
  - `unchanged: int` (nombre de parents inchangés),
  - `deactivated: int` (nombre de parents désactivés),
  - `details: ImportDiffDetailsResponse` contenant les listes détaillées `created` (`list[ParentSummaryResponse]`), `updated` (`list[ParentUpdateDiffResponse]` avec `changes: dict[str, FieldChangeResponse]`), `unchanged` (`list[ParentSummaryResponse]`) et `deactivated` (`list[ParentSummaryResponse]`).
- **Rationale**:
  - L'issue #5 stipule : *"retour du rapport JSON (`total_parents`, `created`, `updated`, `unchanged`, `deactivated`, détail des changements)"*.
  - Exposer les compteurs scalaires au premier niveau (`total_parents`, `created`, `updated`, `unchanged`, `deactivated`) tout en fournissant le détail complet des changements (`details` / `changes`) permet à un workflow n8n de tester immédiatement `{{$json.created}} > 0` ou `{{$json.updated}} > 0` et d'itérer sur les changements détaillés.
- **Alternatives considered**:
  - *Retourner uniquement des listes sans compteurs numériques* : Obligerait n8n à recalculer les longueurs de tableaux et ne fournirait pas la clé `total_parents` demandée dans l'issue #5.
