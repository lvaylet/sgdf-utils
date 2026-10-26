# Spécification Fonctionnelle : Exposition du Service Web d'Intégration des Contacts Parents pour l'Automatisation et la Messagerie

**Feature Branch**: `009-exposer-api-rest-fastapi`

**Created**: 2026-10-26

**Status**: Draft

**Input**: Description utilisateur : "Travaille sur https://github.com/lvaylet/sgdf-utils/issues/5, dans une branche et une Pull Request dédiées, avec des messages de commit en anglais."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import distant d'un export d'adhérents et obtention du rapport de différentiel (Priority: P1)

Un responsable du groupe scout ou un scénario d'automatisation domestique (tel que n8n) peut téléverser directement un fichier d'export des adhérents (`ExportIndividus.xls`) vers le service via une requête réseau (`POST /api/v1/imports/intranet`), déclencher la synchronisation transactionnelle dans le stockage local des contacts parents et recevoir immédiatement un rapport structuré indiquant le nombre total de parents traités, le nombre de créations, de mises à jour, de fiches inchangées et de désactivations, ainsi que le détail complet des changements détectés.

**Why this priority**: Constitue le point d'entrée indispensable pour alimenter et tenir à jour le référentiel des parents à distance depuis un automate sans manipulation manuelle sur le serveur.

**Independent Test**: Peut être testé indépendamment en envoyant le fichier de référence `ExportIndividus.xls` sur une base vierge (qui doit retourner `134` parents créés), puis en le renvoyant une seconde fois (qui doit retourner `134` parents inchangés et `0` modification), et en vérifiant le rejet propre d'un fichier invalide.

**Acceptance Scenarios**:

1. **Given** un service démarré avec une base de contacts vierge, **When** un client autorisé téléverse un fichier `ExportIndividus.xls` valide sur `POST /api/v1/imports/intranet`, **Then** le service synchronise les parents en base et retourne un code de succès (`200`) avec un rapport JSON contenant les compteurs (`total_parents: 134`, `created_count: 134`, `updated_count: 0`, `unchanged_count: 0`, `deactivated_count: 0`) ainsi que les listes détaillées correspondantes (`created`, `updated`, `unchanged`, `deactivated`).
2. **Given** un service dont la base contient déjà les 134 parents de l'export de référence, **When** le même fichier `ExportIndividus.xls` est téléversé à nouveau sur `POST /api/v1/imports/intranet`, **Then** le rapport retourné indique `created_count: 0`, `updated_count: 0`, `unchanged_count: 134`, `deactivated_count: 0`.
3. **Given** un service démarré, **When** un client envoie sur `POST /api/v1/imports/intranet` un fichier vide ou dont les colonnes obligatoires SGDF sont absentes, **Then** le service retourne une erreur client explicite en français (`400` ou `422`) sans altérer les données existantes en base.

---

### User Story 2 - Récupération des destinataires de messagerie par unité et identification d'un parent par numéro de téléphone (Priority: P1)

Un scénario d'automatisation couplé à une passerelle de messagerie WhatsApp (WAHA) peut :
1. Interroger `GET /api/v1/units/{unit_name}/whatsapp-recipients` pour obtenir la liste des parents actifs d'une unité scoute donnée disposant d'un numéro de téléphone portable valide, accompagnés de leur identifiant de discussion prêt à l'emploi (`waha_chat_id` sous la forme `33687966975@c.us`), de leur numéro au format international (`phone_e164`), de leur prénom, de leur nom et de leurs enfants rattachés ;
2. Interroger `GET /api/v1/parents/by-phone/{phone}` lors de la réception d'un message entrant pour identifier immédiatement le parent expéditeur à partir de son numéro au format international (`+336...`), au format national (`06...`) ou directement sous forme d'identifiant de discussion (`336...@c.us`) ;
3. Mettre à jour partiellement les métadonnées d'intégration d'un parent via `PATCH /api/v1/parents/{parent_id}` (notamment l'indicateur `has_whatsapp: true/false`).

**Why this priority**: Permet l'automatisation bidirectionnelle des communications du groupe scout avec les familles (diffusion par unité et identification des réponses entrantes).

**Independent Test**: Peut être testé indépendamment sur une base alimentée en interrogeant les destinataires d'une unité (ex. `LOUVETEAUX-JEANNETTES` ou `LJ`), en recherchant un parent existant sous les trois formats de numéro (`+336...`, `06...`, `336...@c.us`), et en modifiant son statut `has_whatsapp` via `PATCH /api/v1/parents/{parent_id}`.

**Acceptance Scenarios**:

1. **Given** une base contenant des parents rattachés à différentes unités, **When** un client interroge `GET /api/v1/units/{unit_name}/whatsapp-recipients` (avec le nom court ou le libellé d'une unité), **Then** seuls les parents actifs ayant au moins un enfant dans cette unité et disposant d'au moins un numéro mobile valide sont retournés, avec un champ `waha_chat_id` formaté sans le signe `+` suivi de `@c.us` (ex. `33687966975@c.us`), `phone_e164` (ex. `+33687966975`), `first_name`, `last_name` et `children`.
2. **Given** un parent actif enregistré avec le numéro `+33687966975`, **When** un client interroge `GET /api/v1/parents/by-phone/+33687966975`, `GET /api/v1/parents/by-phone/0687966975` ou `GET /api/v1/parents/by-phone/33687966975@c.us`, **Then** le service retrouve et retourne la même fiche parent complète avec son identifiant `id` et ses enfants.
3. **Given** un parent existant d'identifiant `parent_id`, **When** un client envoie `PATCH /api/v1/parents/{parent_id}` avec `{"has_whatsapp": true}`, **Then** la fiche du parent est mise à jour en base avec `has_whatsapp = true` et retournée au client, et cette valeur persiste lors des imports ultérieurs.

---

### User Story 3 - Consultation filtrée des parents et téléchargement à la volée des fichiers de contacts (Priority: P2)

Un responsable ou un outil tiers peut consulter la liste paginée et filtrée des parents via `GET /api/v1/parents` (filtrage par unité `unit`, par présence d'un mobile valide `has_mobile`, par statut d'inscription `registration_status`, par état d'activité `active_only`, avec pagination `limit` et `offset`) et télécharger à la volée les fichiers `ContactParents.vcf` (`GET /api/v1/exports/vcf`) et `ContactsParents.xlsx` (`GET /api/v1/exports/xlsx`) générés directement depuis la base de données, avec la possibilité d'appliquer les mêmes filtres optionnels.

**Why this priority**: Permet aux responsables et aux workflows d'automatisation d'explorer les contacts et de récupérer à tout moment des carnets d'adresses vCard ou Excel complets ou ciblés par unité.

**Independent Test**: Peut être testé indépendamment en appelant `GET /api/v1/parents` avec différentes combinaisons de filtres et de pagination, puis en téléchargeant `/api/v1/exports/vcf` et `/api/v1/exports/xlsx` (sans filtre puis avec filtre `unit`) et en vérifiant les en-têtes de téléchargement et le contenu généré.

**Acceptance Scenarios**:

1. **Given** une base contenant les 134 parents de l'export de référence, **When** un client appelle `GET /api/v1/parents?unit=FARFADETS&has_mobile=true&active_only=true`, **Then** seuls les parents actifs ayant au moins un enfant chez les Farfadets et un numéro de mobile valide sont retournés, triés par ordre alphabétique français.
2. **Given** une base contenant les 134 parents de l'export de référence, **When** un client appelle `GET /api/v1/exports/vcf` et `GET /api/v1/exports/xlsx`, **Then** le service retourne respectivement un flux vCard 3.0 (`text/vcard`, pièce jointe `ContactParents.vcf`) et un classeur Excel (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, pièce jointe `ContactsParents.xlsx`) contenant les 134 parents actifs.
3. **Given** une base alimentée, **When** un client appelle `GET /api/v1/exports/vcf?unit=FARFADETS` ou `GET /api/v1/exports/xlsx?unit=FARFADETS`, **Then** le fichier généré contient uniquement les parents correspondant aux filtres demandés.

---

### User Story 4 - Supervision de santé, documentation interactive et sécurisation par clé d'API (Priority: P1)

L'administrateur du serveur domestique peut superviser la disponibilité du service et de sa base de données via `GET /health` (accessible sans authentification), consulter la spécification OpenAPI interactive sur `/docs` et `/openapi.json`, configurer le service par variables d'environnement (`SGDF_DATABASE_URL`, `SGDF_API_KEY`, `SGDF_HOST`, `SGDF_PORT`) et protéger l'ensemble des routes `/api/v1/*` par une clé d'API transmise dans l'en-tête `X-API-Key` dès lors que `SGDF_API_KEY` est définie.

**Why this priority**: Garantit que les données personnelles des familles du groupe scout ne sont pas exposées sans contrôle d'accès sur le réseau local et que le service est facilement supervisable et intégrable.

**Independent Test**: Peut être testé indépendamment en vérifiant `/health`, `/docs` et `/openapi.json`, puis en testant les routes `/api/v1/*` avec `SGDF_API_KEY` non définie (accès ouvert) et avec `SGDF_API_KEY` définie (rejet `401`/`403` sans clé ou avec une clé erronée, succès `200` avec la clé valide).

**Acceptance Scenarios**:

1. **Given** le service démarré avec une variable `SGDF_API_KEY` configurée et non vide, **When** une requête est envoyée sur n'importe quelle route `/api/v1/*` sans en-tête `X-API-Key` ou avec une clé invalide, **Then** le service refuse l'accès avec un code HTTP `401` (clé absente) ou `403` (clé invalide) et un message d'erreur en français, tandis que `GET /health` reste accessible sans clé et retourne `200`.
2. **Given** le service démarré sans variable `SGDF_API_KEY` (ou avec une valeur vide), **When** une requête est envoyée sur `/api/v1/*` sans en-tête `X-API-Key`, **Then** la requête est acceptée normalement.
3. **Given** le service démarré, **When** un client interroge `GET /health`, **Then** le service vérifie effectivement la connectivité à la base locale et retourne un statut `ok` (`200`).

---

### Edge Cases

- **Numéro de téléphone au format identifiant WhatsApp (`@c.us` ou `@s.whatsapp.net`) ou avec préfixe `0033` / `33`** : Lors d'une recherche sur `GET /api/v1/parents/by-phone/{phone}`, le système doit nettoyer tout suffixe `@c.us` (ou `@s.whatsapp.net`), gérer les espaces ou ponctuations éventuels, et reconnaître aussi bien `33687966975@c.us`, `33687966975`, `+33687966975` que `0687966975`. Si aucun parent ne correspond, le service retourne un code `404` avec un message explicite en français.
- **Parent disposant uniquement d'un mobile secondaire valide** : Pour `GET /api/v1/units/{unit_name}/whatsapp-recipients`, si le mobile principal est vide ou invalide mais que le mobile secondaire est un numéro mobile valide, le service utilise ce numéro mobile valide pour construire `phone_e164` et `waha_chat_id`.
- **Mise à jour ou recherche d'un identifiant de parent inexistant** : Un appel à `PATCH /api/v1/parents/{parent_id}` avec un `parent_id` inconnu doit retourner un code `404` explicite en français.
- **Unité ne comportant aucun parent ou unité inconnue** : Un appel à `GET /api/v1/units/{unit_name}/whatsapp-recipients` ou `GET /api/v1/parents?unit=...` pour une unité sans parent correspondant retourne une liste vide `[]` avec un code `200` (et non une erreur serveur).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT exposer un point d'entrée web REST (`sgdf_contacts/entrypoints/api.py`) publiant automatiquement sa spécification OpenAPI sur `/openapi.json` et sa documentation interactive sur `/docs`.
- **FR-002**: Le système DOIT être configurable via les variables d'environnement suivantes (avec des valeurs par défaut raisonnables) :
  - `SGDF_DATABASE_URL` : chemin ou URL de la base SQLite (par défaut `sqlite:///sgdf_contacts.db`),
  - `SGDF_API_KEY` : clé d'API optionnelle activant l'authentification par en-tête `X-API-Key` lorsqu'elle est définie et non vide,
  - `SGDF_HOST` : adresse d'écoute du serveur (par défaut `127.0.0.1` ou `0.0.0.0`),
  - `SGDF_PORT` : port d'écoute du serveur (par défaut `8000`).
- **FR-003**: Lorsque `SGDF_API_KEY` est définie et non vide, toutes les routes sous `/api/v1/*` DOIVENT exiger l'en-tête HTTP `X-API-Key` correspondant et rejeter les requêtes non autorisées avec un code HTTP `401` ou `403`. Lorsque `SGDF_API_KEY` n'est pas définie (ou est vide), les routes `/api/v1/*` DOIVENT être accessibles sans en-tête `X-API-Key`.
- **FR-004**: Le système DOIT exposer l'endpoint `GET /health` (exempté d'authentification `X-API-Key`) qui exécute une vérification réelle de la connexion à la base de données SQLite et retourne l'état de santé du service (`status: "ok"`, `database: "ok"`).
- **FR-005**: Le système DOIT exposer l'endpoint `POST /api/v1/imports/intranet` acceptant un fichier `ExportIndividus.xls` en téléversement multipart (`file`), exécutant la synchronisation transactionnelle en base et retournant un rapport JSON comprenant les compteurs (`total_parents`, `created`, `updated`, `unchanged`, `deactivated`) ainsi que le détail des parents créés, mis à jour (avec les valeurs avant/après de chaque champ modifié), inchangés et désactivés.
- **FR-006**: Le système DOIT exposer l'endpoint `GET /api/v1/parents` retournant la liste des parents enregistrés (avec leur `id`, leurs coordonnées, leurs métadonnées `has_whatsapp`, `is_active`, `first_seen_at`, `updated_at` et leurs enfants rattachés), en prenant en charge les paramètres de requête optionnels `unit` (code court ou nom d'unité), `has_mobile` (`true`/`false`), `registration_status`, `active_only` (`true` par défaut) ainsi que la pagination (`limit`, `offset`).
- **FR-007**: Le système DOIT exposer l'endpoint `GET /api/v1/units/{unit_name}/whatsapp-recipients` retournant les parents actifs ayant au moins un enfant rattaché à l'unité demandée et possédant un numéro de téléphone mobile valide, chaque élément contenant l'identifiant du parent (`parent_id`), `first_name`, `last_name`, `phone_e164` (ex. `+33687966975`), `waha_chat_id` (ex. `33687966975@c.us`), `has_whatsapp` et la liste `children` des enfants du parent.
- **FR-008**: Le système DOIT exposer l'endpoint `GET /api/v1/parents/by-phone/{phone}` permettant de rechercher un parent à partir d'un numéro de téléphone fourni au format international E.164 (`+336...`), au format national (`06...`), au format numérique international sans `+` (`336...`) ou au format identifiant WAHA (`336...@c.us`), et retournant `404` si aucun parent ne correspond.
- **FR-009**: Le système DOIT exposer l'endpoint `PATCH /api/v1/parents/{parent_id}` permettant de mettre à jour partiellement les métadonnées d'intégration d'un parent (notamment `has_whatsapp: bool | None`) à partir de son identifiant technique `parent_id`, et retournant `404` si l'identifiant n'existe pas.
- **FR-010**: Le système DOIT exposer les endpoints `GET /api/v1/exports/vcf` et `GET /api/v1/exports/xlsx` permettant de télécharger à la volée les fichiers `ContactParents.vcf` et `ContactsParents.xlsx` générés depuis la base de données, avec prise en charge des filtres optionnels (`unit`, `has_mobile`, `registration_status`, `active_only`).
- **FR-011**: Conformément à la constitution du projet, les dépendances nécessaires (`fastapi`, `uvicorn`, `python-multipart`, `httpx`) DOIVENT être déclarées dans `flake.nix` et `devbox.json`, le code source DOIT être intégralement rédigé en anglais, et les commentaires, docstrings, messages d'erreur et la documentation (`README.md`) DOIVENT être rédigés en français.

### Key Entities

- **Fiche Parent API (`ParentResponse`)** : Représentation exposée d'un parent incluant son identifiant unique en base (`id`), ses coordonnées normalisées, ses enfants rattachés (`children`), ses unités (`units`), son statut d'activité (`is_active`), sa métadonnée d'intégration (`has_whatsapp`) et ses horodatages (`first_seen_at`, `updated_at`).
- **Destinataire WhatsApp (`WhatsAppRecipientResponse`)** : Projection dédiée à l'intégration WAHA/n8n associant un parent d'une unité à son numéro mobile E.164 (`phone_e164`), son identifiant de discussion WAHA (`waha_chat_id` au format `<chiffres_e164_sans_plus>@c.us`), son identité et ses enfants.
- **Rapport d'Import (`ImportReportResponse`)** : Synthèse retournée après l'import d'un fichier `ExportIndividus.xls`, exposant les compteurs (`total_parents`, `created`, `updated`, `unchanged`, `deactivated`) et le détail des fiches et des champs modifiés.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Le service démarre sans erreur et expose sa spécification complète sur `/openapi.json` et `/docs`, ainsi qu'un contrôle d'état fonctionnel sur `/health`.
- **SC-002**: L'import via `POST /api/v1/imports/intranet` du fichier de référence `ExportIndividus.xls` traite 100 % des 134 parents en moins de 5 secondes et retourne un rapport exact (`total_parents: 134`, `created: 134` au premier appel, puis `unchanged: 134` au second appel).
- **SC-003**: 100 % des recherches par téléphone sur `GET /api/v1/parents/by-phone/{phone}` aboutissent au même parent que le numéro soit fourni en `+336...`, `06...` ou `336...@c.us`, et 100 % des destinataires retournés par `GET /api/v1/units/{unit_name}/whatsapp-recipients` présentent un `waha_chat_id` valide au format `<chiffres>@c.us`.
- **SC-004**: 100 % des requêtes vers `/api/v1/*` dépourvues d'en-tête `X-API-Key` valide sont rejetées (`401`/`403`) dès qu'une clé `SGDF_API_KEY` est configurée.
- **SC-005**: Les fichiers `ContactParents.vcf` et `ContactsParents.xlsx` téléchargés via `/api/v1/exports/vcf` et `/api/v1/exports/xlsx` sans filtre sur la base alimentée par `ExportIndividus.xls` contiennent exactement les 134 parents actifs.

## Assumptions

- Le champ `total_parents` du rapport d'import retourné par `POST /api/v1/imports/intranet` correspond au nombre total de parents actifs présents dans l'export importé (`len(created) + len(updated) + len(unchanged)`), et le rapport fournit à la fois les compteurs numériques (`total_parents`, `created`, `updated`, `unchanged`, `deactivated`) et le détail des changements (`changes` / listes détaillées) pour faciliter son exploitation dans n8n.
- Pour un parent possédant deux numéros de téléphone portable valides (`primary_mobile_phone` et `secondary_mobile_phone`), l'endpoint `GET /api/v1/units/{unit_name}/whatsapp-recipients` privilégie le portable principal (`primary_mobile_phone`) et se replie sur le portable secondaire si le principal est absent ou non mobile.
- L'adresse d'écoute par défaut est `127.0.0.1` et le port par défaut est `8000` lorsque `SGDF_HOST` et `SGDF_PORT` ne sont pas définis.
