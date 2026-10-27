# Automatisation SGDF La Rochelle — Contacts Parents

Ce dépôt accueille les scripts Python 3 destinés à automatiser les tâches administratives répétitives du groupe scout **Scouts et Guides de France (SGDF) de La Rochelle**, notamment le traitement des exports d'adhérents et des coordonnées des parents pour la mise à jour de **Google Contacts** et la préparation des **groupes WhatsApp d'unités**.

## 1. Environnement de développement éphémère

Pour éviter toute installation manuelle sur le système hôte et garantir la reproductibilité entre bénévoles, le projet fournit **deux définitions d'environnement éphémère maintenues en parallèle**, toutes deux activées automatiquement par `direnv` via le fichier `.envrc` :

1. **Option 1 — Nix Flakes (`flake.nix`)** : Option prioritaire par défaut lorsque `nix` est présent sur la machine.
2. **Option 2 — Jetify Devbox (`devbox.json`)** : Option de repli automatique lorsque seul `devbox` est présent, ou activable à la demande.

### Paquets et outils inclus d'office

Les deux options fournissent exactement le même environnement Python 3 isolé (sans étape `pip install` ni création de `.venv` requise) :

- **Python 3** (`python3`)
- **`pandas`** : Manipulation et croisement des tableaux d'adhérents et de parents
- **`beautifulsoup4`** et **`lxml`** : Analyse des exports SGDF au format HTML portant l'extension `.xls` (ex. `ExportIndividus.xls`)
- **`xlrd`** et **`openpyxl`** : Lecture et génération de classeurs Excel `.xls` et `.xlsx`
- **`sqlmodel`** et **`sqlalchemy`** : Persistance relationnelle locale SQLite (en mode WAL, compatible PostgreSQL) et calcul de différentiel d'import
- **`fastapi`**, **`uvicorn`**, **`python-multipart`** et **`httpx`** : Exposition de l'API HTTP REST avec spécification OpenAPI automatique pour **n8n** et **WAHA**
- **`pytest`** : Exécution des tests automatisés
- **`ruff`** : Vérification de la qualité et du style du code Python

## 2. Activation automatique avec `direnv`

Lors de votre première entrée dans le dossier, autorisez l'exécution du fichier `.envrc` :

```bash
direnv allow
```

Dès cet instant :

- À chaque entrée dans le dossier (`cd contacts-parents`), l'environnement Python 3 éphémère se charge automatiquement.
- À chaque sortie du dossier (`cd ..`), l'environnement est déchargé proprement sans laisser de trace sur le système hôte.

### Basculer entre `flake.nix` et `devbox.json`

Le fichier `.envrc` s'adapte automatiquement aux outils installés sur votre poste via la variable `ENV_TOOL` :

- **Comportement par défaut (`ENV_TOOL=auto`)** : Utilise `flake.nix` si `nix` est installé, sinon bascule automatiquement sur `devbox.json` si `devbox` est installé.
- **Forcer l'utilisation de Nix Flakes (`flake.nix`)** :

  ```bash
  ENV_TOOL=flake direnv reload
  ```

- **Forcer l'utilisation de Jetify Devbox (`devbox.json`)** :

  ```bash
  ENV_TOOL=devbox direnv reload
  ```

- **Enregistrer votre préférence localement** (sans modifier les fichiers suivis par Git) : créez un fichier `.envrc.local` à la racine :

  ```bash
  echo "export ENV_TOOL=devbox" > .envrc.local
  direnv allow
  ```

## 3. Extraction et regroupement des contacts des parents (`extract_parent_contacts.py`)

Le script `extract_parent_contacts.py` lit en lecture seule le fichier d'export SGDF (`ExportIndividus.xls`) et génère le classeur Excel `ContactsParents.xlsx` comprenant :

1. L'onglet **`ExportIndividus`** : copie tabulaire fidèle des données d'origine.
2. L'onglet **`ContactsParents`** : liste des parents dédoublonnés sur `(Nom, Prénom)` et triés par ordre alphabétique français (Nom puis Prénom).

### Colonnes produites dans l'onglet `ContactsParents`

1. **`Nom`** : Nom de famille du parent en minuscules avec initiale(s) en majuscule.
2. **`Prénom`** : Prénom du parent en minuscules avec initiale(s) en majuscule.
3. **`Téléphone portable principal`** : Numéro de portable principal au format international sans espaces (ex. `+33687966975`). Si ce champ est vide mais qu'un numéro de portable valide (`+336` ou `+337`) figure dans le téléphone fixe ou le portable secondaire, il y est automatiquement déplacé (avec priorité au téléphone fixe).
4. **`Téléphone portable secondaire`** : Numéro de portable secondaire au format international sans espaces.
5. **`Téléphone fixe (domicile)`** : Numéro de téléphone fixe domicile au format international sans espaces (ex. `+33546123456`).
6. **`Adresse email`** : Adresse courriel personnelle (ou dédiée SGDF en repli).
7. **`Noms des enfants`** : Liste des enfants regroupés sous la forme `Prénom Nom`, séparés par des virgules (ex. `Lucas Bernard, Chloé Bernard`).
8. **`Unités des enfants`** : Unités courtes des enfants dans le même ordre que les enfants eux-mêmes (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`).
9. **`Rue`** : Lignes d'adresse postale (`Ligne 1`, `Ligne 2`, `Ligne 3`) non vides normalisées en casse titre (minuscules avec la première lettre de chaque mot en majuscule) et séparées par `, `.
10. **`Code postal`** : Code postal de l'adresse du parent.
11. **`Ville`** : Municipalité de l'adresse du parent normalisée en casse titre (minuscules avec la première lettre de chaque mot en majuscule, ex. `La Rochelle`).
12. **`Numéro d'adhérent`** : Numéro d'adhérent SGDF du parent (issu de sa fiche représentant légal ou de son inscription adulte).
13. **`Remarques`** : Rôle éventuel du parent au sein du groupe (ex. `Parent Animateur Farfadet`, `Responsable de groupe`, délégations) et statut d'inscription des enfants s'il diffère de `Inscrit(e)` (`Pré-inscrit(e)` ou `Invité(e)`).

### Commandes d'utilisation

```bash
# Exécution standard (lit ExportIndividus.xls et génère ContactsParents.xlsx)
python3 extract_parent_contacts.py

# Exécution avec chemins personnalisés
python3 extract_parent_contacts.py --input ExportIndividus.xls --output ContactsParents.xlsx

# Afficher l'aide en français
python3 extract_parent_contacts.py --help
```

## 4. Génération du fichier d'import Google Contacts (`generate_contacts_vcf.py`)

Le script `generate_contacts_vcf.py` lit en lecture seule l'onglet `ContactsParents` du classeur `ContactsParents.xlsx` et génère le fichier **`ContactParents.vcf`** (au format standard vCard 3.0 encodé en UTF-8) directement importable dans Google Contacts.

### Contenu de chaque fiche dans `ContactParents.vcf`

- **Identité** : Nom structuré (`Nom`, `Prénom`) et nom complet affiché sous la forme `Prénom Nom`.
- **Numéros de téléphone** : Téléphone portable principal (mobile préféré), téléphone portable secondaire et téléphone fixe domicile (lorsqu'ils sont renseignés).
- **Adresse email** : Adresse courriel du parent (lorsqu'elle est renseignée).
- **Adresse physique (`ADR`)** : Adresse postale structurée construite directement à partir des colonnes `Rue`, `Code postal` et `Ville` (lorsqu'elle est renseignée).
- **Informations complémentaires (`NOTE`)** :
  - `Enfants : Prénom Nom (Unité), ...`
  - `Numéro d'adhérent : <numéro>` (uniquement s'il existe)
  - `Remarques : <remarques>` (uniquement si elles existent)
- **Étiquettes Google Contacts (`CATEGORIES`)** : Tous les parents reçoivent automatiquement les deux étiquettes **`SGDF`** et **`La Rochelle`**.

### Commandes d'utilisation

```bash
# Exécution standard (lit ContactsParents.xlsx et génère ContactParents.vcf)
python3 generate_contacts_vcf.py

# Exécution avec chemins personnalisés
python3 generate_contacts_vcf.py --input ContactsParents.xlsx --output ContactParents.vcf

# Afficher l'aide en français
python3 generate_contacts_vcf.py --help
```

## 5. Architecture modulaire du package `sgdf_contacts`

La logique métier et technique est mutualisée dans le package Python `sgdf_contacts/` afin d'éliminer toute duplication entre les scripts CLI (`extract_parent_contacts.py` et `generate_contacts_vcf.py`) et de permettre une utilisation directe en mémoire :

- **`sgdf_contacts/domain/`** : Cœur métier pur (sans dépendance externe) regroupant les entités (`ParentContact` avec la propriété `waha_chat_id`, `AttachedChild`, `AdultGroupProfile`, `ParentContactCard`), les constantes partagées (`PARENT_CONTACTS_HEADERS`, `ADULT_ROLE_LABELS`, `DEFAULT_CATEGORIES`), les exceptions métier et les fonctions pures de normalisation et de tri.
- **`sgdf_contacts/parsers/`** : Lecture de l'export `ExportIndividus.xls` (`read_individuals_export_table`, acceptant un `Path` ou un flux `bytes`/`io.BytesIO` en mémoire), extraction/dédoublonnage (`extract_and_group_parents`) et lecture du classeur `ContactsParents.xlsx` (`read_parent_contacts_excel`).
- **`sgdf_contacts/exporters/`** : Génération du classeur Excel (`write_parent_contacts_workbook`, sur disque `Path` ou en mémoire `io.BytesIO`) et génération vCard 3.0 (`format_parent_vcard`, `format_vcf_content`, `write_vcf_file`, directement depuis `list[ParentContact]` ou `list[ParentContactCard]`).
- **`sgdf_contacts/persistence/`** : Persistance locale SQLite en mode WAL (`create_db_engine`, `init_db`, tables `parents`, `children`, `parent_child_links` via `SQLModel`) et dépôt `ParentContactRepository` offrant :
  - l'import transactionnel idempotent (`sync_parents`, `import_individuals_xls`) avec calcul automatique de différentiel (`ImportDiffReport` : `created`, `updated` avec détail des champs modifiés via `FieldChange`, `unchanged`, `deactivated` sans perte des métadonnées externes comme `has_whatsapp`),
  - le requêtage et le filtrage (`list_active_parents`, `filter_parents` par unité courte, statut d'inscription ou présence d'un portable valide, `find_by_phone`),
  - la régénération directe de `ContactParents.vcf` (`export_vcf`) et de `ContactsParents.xlsx` (`export_excel`) depuis la base SQLite sans relire `ExportIndividus.xls`.
- **`sgdf_contacts/entrypoints/`** : Points d'entrée exécutables déclarés dans `pyproject.toml` :
  - `sgdf_contacts/entrypoints/cli_extract.py` (`sgdf-extract`),
  - `sgdf_contacts/entrypoints/cli_vcf.py` (`sgdf-vcf`),
  - `sgdf_contacts/entrypoints/api.py` (`sgdf-api`) : API HTTP REST (`FastAPI`) dotée d'une spécification OpenAPI automatique (`/docs`, `/openapi.json`) pour l'intégration avec **n8n** et **WAHA**.

## 6. API HTTP REST pour n8n et WAHA (`sgdf_contacts.entrypoints.api`)

Le module `sgdf_contacts/entrypoints/api.py` expose le référentiel SQLite des parents via HTTP REST.

### Configuration par variables d'environnement

- **`SGDF_DATABASE_URL`** : Chemin ou URL SQLAlchemy de la base SQLite (par défaut `sqlite:///sgdf_contacts.db`).
- **`SGDF_API_KEY`** : Clé secrète optionnelle activant l'authentification par en-tête `X-API-Key` sur toutes les routes `/api/v1/*` dès qu'elle est définie.
- **`SGDF_HOST`** : Adresse d'écoute du serveur (par défaut `127.0.0.1`).
- **`SGDF_PORT`** : Port d'écoute du serveur (par défaut `8000`).

### Démarrage du serveur

```bash
# Démarrage direct via Nix
nix run .#sgdf-api

# Ou via la commande installée par le paquet Python
sgdf-api

# Ou avec uvicorn / le module Python (utilise SGDF_HOST et SGDF_PORT)
uvicorn sgdf_contacts.entrypoints.api:app --host 0.0.0.0 --port 8000
python3 -m sgdf_contacts.entrypoints.api
```

### Endpoints exposés

- **`GET /health`** : Vérification publique de l'état du service et de la connexion SQLite.
- **`POST /api/v1/imports/intranet`** : Téléversement multipart (`file`) d'un fichier `ExportIndividus.xls`, synchronisation transactionnelle en base et retour du rapport JSON (`total_parents`, `created`, `updated`, `unchanged`, `deactivated` et `changes`).
- **`GET /api/v1/parents`** : Liste filtrée et paginée des parents (`?unit=...`, `?has_mobile=true`, `?registration_status=...`, `?active_only=true`, `?limit=...`, `?offset=...`).
- **`GET /api/v1/units/{unit_name}/whatsapp-recipients`** : Destinataires WhatsApp actifs d'une unité disposant d'un numéro mobile valide, formatés pour **WAHA** (`waha_chat_id` au format `33687966975@c.us`, `phone_e164`, `first_name`, `last_name`, `children`).
- **`GET /api/v1/parents/by-phone/{phone}`** : Recherche d'un parent à partir d'un numéro au format E.164 (`+336...`), national (`06...`), international sans `+` (`336...`) ou identifiant WAHA (`336...@c.us`).
- **`PATCH /api/v1/parents/{parent_id}`** : Mise à jour partielle des métadonnées d'intégration (ex. `{"has_whatsapp": true}`).
- **`GET /api/v1/exports/vcf`** et **`GET /api/v1/exports/xlsx`** : Téléchargement à la volée des fichiers `ContactParents.vcf` et `ContactsParents.xlsx` générés depuis la base (avec filtres optionnels).

## 7. Packaging Nix, Déploiement NixOS Homelab et Intégration n8n / WAHA

### 7.1. Paquet Python Nix (`pyproject.toml` + `buildPythonApplication`) et image OCI

Le fichier `pyproject.toml` déclare le paquet `sgdf-contacts` et trois exécutables console (`sgdf-extract`, `sgdf-vcf`, `sgdf-api`), construits et vérifiés dans le bac à sable Nix par `flake.nix` :

```bash
# Construire le paquet Python (exécute automatiquement pytest dans checkPhase)
nix build
./result/bin/sgdf-extract --help
./result/bin/sgdf-vcf --help
./result/bin/sgdf-api

# Lancer directement les applications via nix run
nix run .#sgdf-api
nix run .#sgdf-extract -- --help
nix run .#sgdf-vcf -- --help

# Construire l'image conteneur OCI minimale (sur Linux, pour Podman / Docker)
nix build .#oci-image
podman load < ./result

# Valider le flake complet (paquet, image OCI et évaluation du module NixOS)
nix flake check
```

### 7.2. Déploiement déclaratif sur le Homelab NixOS (`nixosModules.default`)

Pour déployer le service sur un serveur NixOS aux côtés de **n8n** et **WAHA**, ajoutez `sgdf-utils` dans les `inputs` du `flake.nix` de votre homelab et importez `sgdf-utils.nixosModules.default` :

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    sops-nix.url = "github:Mic92/sops-nix";
    sgdf-utils.url = "github:lvaylet/sgdf-utils";
  };

  outputs = { self, nixpkgs, sops-nix, sgdf-utils, ... }: {
    nixosConfigurations.homelab = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        sops-nix.nixosModules.sops
        sgdf-utils.nixosModules.default
        ({ config, ... }: {
          # Secret géré par sops-nix ou agenix contenant : SGDF_API_KEY=votre-cle-secrete
          sops.secrets."sgdf-utils/env" = { };

          services.sgdf-utils = {
            enable = true;
            host = "127.0.0.1";
            port = 8000;
            dataDir = "/var/lib/sgdf-utils";
            environmentFile = config.sops.secrets."sgdf-utils/env".path;
          };
        })
      ];
    };
  };
}
```

Le module `services.sgdf-utils` génère automatiquement une unité `systemd.services.sgdf-utils` durcie :
- `DynamicUser = true` et `StateDirectory = "sgdf-utils"` (persistance automatique de `/var/lib/sgdf-utils/sgdf.sqlite3`),
- `ProtectSystem = "strict"`, `ProtectHome = true`, `PrivateTmp = true`, `NoNewPrivileges = true`,
- injection sécurisée de `SGDF_API_KEY` via `EnvironmentFile` sans exposition dans `/nix/store`.

### 7.3. Exemples de configuration de workflows n8n et WAHA

Dans **n8n**, créez un identifiant d'authentification (*Header Auth*) nommé `SGDF API Key` avec :
- **Name** : `X-API-Key`
- **Value** : `<valeur de SGDF_API_KEY>`

#### Scénario 1 — Synchronisation automatique d'un export `ExportIndividus.xls`

- **Nœud n8n HTTP Request** :
  - **Method** : `POST`
  - **URL** : `http://127.0.0.1:8000/api/v1/imports/intranet`
  - **Authentication** : *Header Auth* (`X-API-Key`)
  - **Body Content Type** : `Form-Data (Multipart)`
  - **Parameter Type** : *n8n Binary File* (`Input Data Field Name` : `data`, `Name` : `file`)
- **Exploitation de la réponse JSON** :
  - `{{ $json.total_parents }}` : nombre total de parents actifs dans l'export
  - `{{ $json.created }}` / `{{ $json.updated }}` / `{{ $json.deactivated }}` : compteurs de changements permettant de déclencher une notification s'il y a de nouvelles inscriptions ou des modifications de coordonnées (`{{ $json.changes.updated }}`).

#### Scénario 2 — Diffusion d'un message WhatsApp aux parents d'une unité via WAHA

1. **Nœud n8n HTTP Request (Récupération des destinataires)** :
   - **Method** : `GET`
   - **URL** : `http://127.0.0.1:8000/api/v1/units/FARFADETS/whatsapp-recipients` (ou `LJ`, `SG`, `PC`, `COMPAGNONS`)
   - **Authentication** : *Header Auth* (`X-API-Key`)
2. **Nœud n8n HTTP Request / WAHA (Envoi du message)** pour chaque élément retourné :
   - **Method** : `POST`
   - **URL** : `http://127.0.0.1:3000/api/sendText`
   - **Body JSON** :
     ```json
     {
       "session": "default",
       "chatId": "{{ $json.waha_chat_id }}",
       "text": "Bonjour {{ $json.first_name }}, rappel pour la sortie de ce week-end !"
     }
     ```

#### Scénario 3 — Identification d'un parent sur réception d'un message entrant WAHA et mise à jour de `has_whatsapp`

1. **Webhook WAHA (`message`)** reçu dans n8n contenant `{{ $json.payload.from }}` (ex. `33687966975@c.us`).
2. **Nœud n8n HTTP Request (Identification du parent)** :
   - **Method** : `GET`
   - **URL** : `http://127.0.0.1:8000/api/v1/parents/by-phone/{{ encodeURIComponent($json.payload.from) }}`
   - **Authentication** : *Header Auth* (`X-API-Key`)
3. **Nœud n8n HTTP Request (Confirmation de la présence WhatsApp)** :
   - **Method** : `PATCH`
   - **URL** : `http://127.0.0.1:8000/api/v1/parents/{{ $json.id }}`
   - **Body JSON** : `{"has_whatsapp": true}`

## 8. Vérification et tests

Une fois dans le dossier (avec l'environnement actif), vous pouvez vérifier le bon fonctionnement de l'installation et la conformité du code :

```bash
# Exécuter la suite de tests automatisés
pytest -v

# Vérifier la qualité et le style du code Python
ruff check .

# Valider le flake Nix complet et le module NixOS
nix flake check
```

## 9. Confidentialité des données (RGPD)

Conformément à la constitution du projet :

- Les fichiers d'export, de sortie et de bases de données locales (`ExportIndividus.xls`, `ContactsParents.xlsx`, `ContactParents.vcf`, `*.xls`, `*.xlsx`, `*.csv`, `*.vcf`, `*.db`, `*.sqlite`, `*.sqlite3`) contiennent des données personnelles et sont **exclus du suivi Git** via `.gitignore`.
- Les scripts traitent toujours les fichiers d'entrée en **lecture seule**.
