# Contrat d'Interface : API HTTP REST (`sgdf_contacts.entrypoints.api`)

**Feature**: `009-exposer-api-rest-fastapi` | **Date**: 2026-10-26

## 1. Point d'Entrée et Configuration

- **Module Python** : `sgdf_contacts.entrypoints.api`
- **Objets exposés** :
  - `app: FastAPI` : instance prête à l'emploi pour `uvicorn sgdf_contacts.entrypoints.api:app`
  - `create_app(database_url: str | Path | None = None, api_key: str | None = None) -> FastAPI` : fabrique d'application permettant d'injecter une base ou une clé d'API spécifique (notamment dans `pytest`).
- **Variables d'environnement** :
  - `SGDF_DATABASE_URL` (défaut : `sqlite:///sgdf_contacts.db`)
  - `SGDF_API_KEY` (défaut : non défini / vide → authentification désactivée)
  - `SGDF_HOST` (défaut : `127.0.0.1`)
  - `SGDF_PORT` (défaut : `8000`)
- **Documentation OpenAPI automatique** :
  - `GET /openapi.json` : schéma OpenAPI 3.x complet
  - `GET /docs` : interface Swagger UI interactive

---

## 2. Authentification (`X-API-Key`)

- **Portée** : Toutes les routes préfixées par `/api/v1/`. La route `GET /health` ainsi que `/docs` et `/openapi.json` restent publiques.
- **Comportement** :
  - Si `SGDF_API_KEY` n'est pas définie ou est vide : aucune vérification n'est effectuée, les requêtes sur `/api/v1/*` sont autorisées.
  - Si `SGDF_API_KEY` est définie et non vide :
    - Requête sans en-tête `X-API-Key` (ou vide) → `401 Unauthorized` (`{"detail": "Clé d'API manquante dans l'en-tête X-API-Key."}`).
    - Requête avec un en-tête `X-API-Key` différent de `SGDF_API_KEY` → `403 Forbidden` (`{"detail": "Clé d'API invalide."}`).
    - Requête avec un en-tête `X-API-Key` égal à `SGDF_API_KEY` → requête autorisée.

---

## 3. Spécification des Endpoints HTTP

### 3.1 `GET /health`

Vérifie l'état du service et exécute une requête de contrôle sur la connexion SQLite.

- **Authentification** : Aucune
- **Réponse `200 OK`** :
  ```json
  {
    "status": "ok",
    "database": "ok"
  }
  ```

---

### 3.2 `POST /api/v1/imports/intranet`

Téléverse un fichier `ExportIndividus.xls` en `multipart/form-data` (champ `file`), exécute l'upsert transactionnel en base et retourne le rapport de différentiel.

- **Requête** : `Content-Type: multipart/form-data`, champ `file` contenant le fichier `ExportIndividus.xls`.
- **Réponse `200 OK`** :
  ```json
  {
    "total_parents": 134,
    "created": 134,
    "updated": 0,
    "unchanged": 0,
    "deactivated": 0,
    "changes": {
      "created": [ ... ],
      "updated": [
        {
          "parent": { ... },
          "changes": {
            "primary_mobile_phone": {
              "old_value": "+33600000000",
              "new_value": "+33687966975"
            }
          }
        }
      ],
      "unchanged": [ ... ],
      "deactivated": [ ... ]
    }
  }
  ```
- **Erreurs** :
  - `400 Bad Request` : Fichier vide, format HTML/XLS illisible ou colonnes obligatoires SGDF manquantes (`MissingRequiredColumnsError` / `SgdfContactsError`).

---

### 3.3 `GET /api/v1/parents`

Retourne la liste filtrée et paginée des parents stockés en base, triée selon l'ordre alphabétique français.

- **Paramètres de requête (Query Parameters)** :
  - `unit: str | None = None` : Filtre les parents ayant au moins un enfant dans cette unité (accepte le code court ex. `LJ`, `FARFADETS` ou le nom complet).
  - `has_mobile: bool | None = None` : Filtre selon la présence (`true`) ou l'absence (`false`) d'au moins un numéro mobile valide.
  - `registration_status: str | None = None` : Filtre selon le statut d'inscription d'au moins un enfant (ex. `Inscrit(e)`, `Pré-inscrit(e)`).
  - `active_only: bool = True` : Si `true` (défaut), retourne uniquement les parents actifs (`is_active=True`) ; si `false`, inclut aussi les parents désactivés.
  - `limit: int | None = Query(default=None, ge=1)` : Nombre maximal d'éléments retournés (si omis, retourne tous les parents correspondants).
  - `offset: int = Query(default=0, ge=0)` : Décalage de départ pour la pagination.
- **Réponse `200 OK`** : `list[ParentResponse]`

---

### 3.4 `GET /api/v1/units/{unit_name}/whatsapp-recipients`

Retourne les parents actifs de l'unité `{unit_name}` disposant d'un numéro de téléphone mobile valide, avec leur identifiant formaté pour **WAHA**.

- **Paramètre de chemin** :
  - `unit_name: str` : Nom ou code court de l'unité (ex. `FARFADETS`, `LOUVETEAUX-JEANNETTES`, `LJ`, `SG`, `PIOK`).
- **Réponse `200 OK`** : `list[WhatsAppRecipientResponse]`
  ```json
  [
    {
      "parent_id": 1,
      "first_name": "Jean",
      "last_name": "Martin",
      "full_name": "Jean Martin",
      "phone_e164": "+33687966975",
      "waha_chat_id": "33687966975@c.us",
      "has_whatsapp": true,
      "children": [
        {
          "first_name": "Léo",
          "last_name": "Martin",
          "full_name": "Léo Martin",
          "short_unit": "FARFADETS",
          "registration_status": "Inscrit(e)"
        }
      ]
    }
  ]
  ```

---

### 3.5 `GET /api/v1/parents/by-phone/{phone}`

Recherche un parent actif à partir d'un numéro de téléphone au format E.164 (`+33687966975`), national (`0687966975`), international sans `+` (`33687966975`) ou identifiant WAHA (`33687966975@c.us`).

- **Paramètre de chemin** :
  - `phone: str` : Numéro ou identifiant WAHA à rechercher.
- **Paramètre de requête optionnel** :
  - `active_only: bool = True`
- **Réponse `200 OK`** : `ParentResponse`
- **Erreur `404 Not Found`** : Aucun parent trouvé pour ce numéro.

---

### 3.6 `PATCH /api/v1/parents/{parent_id}`

Met à jour partiellement les métadonnées d'intégration d'un parent (ex. `has_whatsapp`).

- **Paramètre de chemin** :
  - `parent_id: int` : Identifiant technique du parent (`parents.id`).
- **Corps JSON** :
  ```json
  {
    "has_whatsapp": true
  }
  ```
- **Réponse `200 OK`** : `ParentResponse` mis à jour.
- **Erreur `404 Not Found`** : Aucun parent trouvé avec cet identifiant `parent_id`.

---

### 3.7 `GET /api/v1/exports/vcf` et `GET /api/v1/exports/xlsx`

Génèrent et téléchargent à la volée respectivement `ContactParents.vcf` et `ContactsParents.xlsx` depuis la base de données, avec prise en charge des filtres optionnels (`unit`, `has_mobile`, `registration_status`, `active_only`).

- **`GET /api/v1/exports/vcf`** :
  - `Content-Type: text/vcard; charset=utf-8`
  - `Content-Disposition: attachment; filename="ContactParents.vcf"`
- **`GET /api/v1/exports/xlsx`** :
  - `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `Content-Disposition: attachment; filename="ContactsParents.xlsx"`
