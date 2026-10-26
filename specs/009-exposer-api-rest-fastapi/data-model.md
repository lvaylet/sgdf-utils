# Data Model: Schémas API HTTP REST (`FastAPI`) et Objets de Transfert

**Feature**: `009-exposer-api-rest-fastapi` | **Date**: 2026-10-26

## 1. Configuration du Service (`ApiSettings`)

| Variable d'environnement | Attribut Python | Valeur par défaut | Description |
|--------------------------|-----------------|-------------------|-------------|
| `SGDF_DATABASE_URL` | `database_url: str` | `"sqlite:///sgdf_contacts.db"` | URL ou chemin de la base SQLite |
| `SGDF_API_KEY` | `api_key: str | None` | `None` | Clé secrète attendue dans l'en-tête `X-API-Key` sur `/api/v1/*` (désactivée si `None` ou vide) |
| `SGDF_HOST` | `host: str` | `"127.0.0.1"` | Adresse IP d'écoute du serveur Uvicorn |
| `SGDF_PORT` | `port: int` | `8000` | Port TCP d'écoute du serveur Uvicorn |

---

## 2. Schémas de Réponse et de Requête (`sgdf_contacts/entrypoints/api.py`)

### 2.1 `HealthResponse` (`GET /health`)

| Champ | Type JSON / Python | Description |
|-------|--------------------|-------------|
| `status` | `str` (`"ok"`) | État global du service HTTP |
| `database` | `str` (`"ok"`) | État de la connexion SQLite (vérifié par une requête `SELECT 1`) |

### 2.2 `ChildResponse`

Représentation d'un enfant rattaché à un parent dans les réponses de l'API.

| Champ | Type JSON / Python | Description |
|-------|--------------------|-------------|
| `first_name` | `str` | Prénom normalisé de l'enfant |
| `last_name` | `str` | Nom de famille normalisé de l'enfant |
| `full_name` | `str` | Nom complet formaté (`"Prénom Nom"`) |
| `short_unit` | `str` | Unité scoute courte (ex. `"LOUVETEAUX-JEANNETTES"`, `"FARFADETS"`) |
| `registration_status` | `str` | Statut d'inscription (ex. `"Inscrit(e)"`, `"Pré-inscrit(e)"`) |

### 2.3 `ParentResponse` (`GET /api/v1/parents`, `GET /api/v1/parents/by-phone/{phone}`, `PATCH /api/v1/parents/{parent_id}`)

Représentation complète d'une fiche parent persistée en base.

| Champ | Type JSON / Python | Description |
|-------|--------------------|-------------|
| `id` | `int` | Identifiant technique unique du parent en base (`parents.id`) |
| `member_id` | `str` | Numéro d'adhérent SGDF du parent (chaîne vide si non adhérent) |
| `last_name` | `str` | Nom de famille normalisé |
| `first_name` | `str` | Prénom normalisé |
| `full_name` | `str` | Nom complet (`"Prénom Nom"`) |
| `primary_mobile_phone` | `str` | Téléphone portable principal au format E.164 (`+336...` / `+337...` ou `""`) |
| `secondary_mobile_phone` | `str` | Téléphone portable secondaire au format E.164 |
| `landline_phone` | `str` | Téléphone fixe au format E.164 |
| `email_address` | `str` | Adresse courriel normalisée |
| `street` | `str` | Rue normalisée |
| `postal_code` | `str` | Code postal normalisé |
| `city` | `str` | Ville normalisée |
| `notes` | `str` | Remarques consolidées |
| `has_whatsapp` | `bool | None` | Statut d'intégration WhatsApp (`true`, `false` ou `null`) |
| `is_active` | `bool` | Indique si le parent est actif dans le dernier import |
| `first_seen_at` | `datetime` | Date/heure UTC de première apparition |
| `updated_at` | `datetime` | Date/heure UTC de dernière modification |
| `units` | `list[str]` | Liste ordonnée et dédoublonnée des unités courtes des enfants |
| `children` | `list[ChildResponse]` | Liste ordonnée des enfants rattachés au parent |

### 2.4 `ParentPatchRequest` (`PATCH /api/v1/parents/{parent_id}`)

Corps JSON de mise à jour partielle des métadonnées d'intégration d'un parent.

| Champ | Type JSON / Python | Description |
|-------|--------------------|-------------|
| `has_whatsapp` | `bool | None` | Nouveau statut WhatsApp du parent (`true`, `false` ou `null`) |

### 2.5 `WhatsAppRecipientResponse` (`GET /api/v1/units/{unit_name}/whatsapp-recipients`)

Représentation d'un parent destinataire WhatsApp pour une unité donnée, prête pour WAHA et n8n.

| Champ | Type JSON / Python | Description |
|-------|--------------------|-------------|
| `parent_id` | `int` | Identifiant technique du parent en base |
| `first_name` | `str` | Prénom du parent |
| `last_name` | `str` | Nom de famille du parent |
| `full_name` | `str` | Nom complet du parent (`"Prénom Nom"`) |
| `phone_e164` | `str` | Numéro de téléphone mobile valide au format E.164 (ex. `"+33687966975"`) |
| `waha_chat_id` | `str` | Identifiant de discussion WAHA (ex. `"33687966975@c.us"`) |
| `has_whatsapp` | `bool | None` | Indicateur `has_whatsapp` enregistré en base |
| `children` | `list[ChildResponse]` | Enfants rattachés au parent |

### 2.6 `ImportReportResponse` (`POST /api/v1/imports/intranet`)

Rapport retourné après l'import d'un fichier `ExportIndividus.xls`.

| Champ | Type JSON / Python | Description |
|-------|--------------------|-------------|
| `total_parents` | `int` | Nombre total de parents actifs présents dans l'export (`created + updated + unchanged`) |
| `created` | `int` | Nombre de nouveaux parents créés |
| `updated` | `int` | Nombre de parents existants mis à jour |
| `unchanged` | `int` | Nombre de parents inchangés |
| `deactivated` | `int` | Nombre de parents précédemment actifs désactivés |
| `changes` | `ImportDiffDetailsResponse` | Détail complet des fiches créées, mises à jour (avec `old_value` / `new_value` par champ), inchangées et désactivées |
