# Spécification Fonctionnelle : Empaquetage de l'Application et Module de Déploiement Déclaratif pour Serveur Domestique

**Feature Branch**: `010-packager-flake-module-nixos`

**Created**: 2026-10-27

**Status**: Draft

**Input**: Description utilisateur : "Travaille sur https://github.com/lvaylet/sgdf-utils/issues/6, avec une Pull Request dédiée et des messages de commit en anglais."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Empaquetage standard de l'application et exécution directe des commandes (`sgdf-extract`, `sgdf-vcf`, `sgdf-api`) (Priority: P1)

Un responsable technique ou un administrateur peut construire et installer l'application sous forme de paquet autonome vérifié par sa suite de tests automatisés, et disposer immédiatement de trois commandes exécutables prêtes à l'emploi :
- `sgdf-extract` pour extraire et regrouper les contacts parents depuis un fichier `ExportIndividus.xls` vers `ContactsParents.xlsx`,
- `sgdf-vcf` pour générer le carnet d'adresses `ContactParents.vcf` depuis `ContactsParents.xlsx`,
- `sgdf-api` (ainsi que `nix run .#sgdf-api`) pour démarrer le serveur HTTP REST exposant le référentiel des parents.

**Why this priority**: Fournit le livrable exécutable reproductible et testé qui sert de socle à la fois à l'utilisation en ligne de commande, au service système déclaratif et à l'image conteneur.

**Independent Test**: Peut être testé indépendamment en lançant `nix build` (qui doit construire le paquet et exécuter l'intégralité des tests dans un environnement isolé), en vérifiant la présence et le fonctionnement de `result/bin/sgdf-extract --help`, `result/bin/sgdf-vcf --help` et `result/bin/sgdf-api`, ainsi que l'exécution directe via `nix run .#sgdf-api`.

**Acceptance Scenarios**:

1. **Given** le code source du dépôt, **When** l'administrateur exécute `nix build`, **Then** le paquet applicatif `sgdf-contacts` est construit, la suite complète de tests automatisés est exécutée pendant la phase de vérification de la construction, et le dossier `result/bin/` expose les trois exécutables `sgdf-extract`, `sgdf-vcf` et `sgdf-api`.
2. **Given** le paquet construit, **When** l'utilisateur invoque `sgdf-extract --help` ou `sgdf-vcf --help`, **Then** chaque commande affiche son aide en français et accepte les mêmes options (`-i/--input`, `-o/--output`) que les scripts historiques `extract_parent_contacts.py` et `generate_contacts_vcf.py` (qui restent rétrocompatibles).
3. **Given** le dépôt du projet, **When** l'administrateur exécute `nix run .#sgdf-api` (avec un port libre configuré via `SGDF_PORT`), **Then** le serveur HTTP REST démarre et répond avec succès (`200 OK`) sur `GET /health`.

---

### User Story 2 - Déploiement déclaratif et durci du service sur un serveur NixOS (`nixosModules.default`) (Priority: P1)

L'administrateur du serveur domestique NixOS peut importer le module déclaratif `nixosModules.default` dans la configuration de sa machine et activer le service via `services.sgdf-utils.enable = true`, en personnalisant au besoin l'adresse d'écoute (`host`), le port (`port`), le répertoire de données (`dataDir`) et le fichier d'environnement contenant les secrets (`environmentFile` pour `SGDF_API_KEY`). Le service système associé est automatiquement durci (`DynamicUser`, isolation du système de fichiers et du réseau local, gestion automatique de `/var/lib/sgdf-utils/sgdf.sqlite3`).

**Why this priority**: Permet une mise en production déclarative, reproductible, sans maintenance manuelle et sécurisée des données personnelles des familles sur le serveur domestique aux côtés de n8n et WAHA.

**Independent Test**: Peut être testé indépendamment en évaluant une configuration NixOS de test important `nixosModules.default` avec `services.sgdf-utils.enable = true` (via `nix flake check`), et en vérifiant les propriétés de l'unité `systemd.services.sgdf-utils` générée (variables d'environnement `SGDF_HOST`, `SGDF_PORT`, `SGDF_DATABASE_URL`, `EnvironmentFile`, et directives de durcissement `DynamicUser`, `StateDirectory`, `ProtectSystem`, `ProtectHome`, `PrivateTmp`, `NoNewPrivileges`).

**Acceptance Scenarios**:

1. **Given** une configuration NixOS important `nixosModules.default` avec uniquement `services.sgdf-utils.enable = true`, **When** la configuration du système est évaluée, **Then** une unité `systemd.services.sgdf-utils` est définie avec les valeurs par défaut (`host = "127.0.0.1"`, `port = 8000`, `dataDir = "/var/lib/sgdf-utils"`, `SGDF_DATABASE_URL = "sqlite:////var/lib/sgdf-utils/sgdf.sqlite3"`) et lance `sgdf-api`.
2. **Given** une configuration NixOS définissant `services.sgdf-utils.environmentFile = "/run/secrets/sgdf-utils.env"`, **When** l'unité `systemd.services.sgdf-utils` est évaluée, **Then** `serviceConfig.EnvironmentFile` pointe vers `/run/secrets/sgdf-utils.env` sans jamais exposer `SGDF_API_KEY` en clair dans le magasin Nix (`/nix/store`).
3. **Given** l'unité `systemd.services.sgdf-utils` activée, **When** ses paramètres de sécurité sont inspectés, **Then** les directives `DynamicUser = true`, `StateDirectory = "sgdf-utils"`, `ProtectSystem = "strict"`, `ProtectHome = true`, `PrivateTmp = true` et `NoNewPrivileges = true` sont toutes actives.

---

### User Story 3 - Construction d'image conteneur OCI et validation globale du Flake (`packages.oci-image` & `nix flake check`) (Priority: P2)

L'administrateur peut construire une image conteneur OCI minimale (`nix build .#oci-image`) prête à être chargée dans Podman ou Docker si le déploiement conteneurisé est privilégié, et peut valider d'une seule commande (`nix flake check`) l'intégralité du dépôt (paquet principal, points d'entrée, image OCI et évaluation du module NixOS).

**Why this priority**: Offre une alternative de déploiement conteneurisée pour les environnements Podman/Docker et garantit l'absence de régression sur le flake et le module NixOS.

**Independent Test**: Peut être testé indépendamment en exécutant `nix build .#oci-image` (sur Linux) pour vérifier la génération de l'archive d'image OCI et `nix flake check` pour valider toutes les sorties du flake.

**Acceptance Scenarios**:

1. **Given** un système Linux avec Nix, **When** l'administrateur exécute `nix build .#oci-image`, **Then** Nix produit une archive d'image OCI minimale contenant `sgdf-api` comme point d'entrée par défaut et exposant le port `8000`.
2. **Given** le dépôt du projet, **When** l'administrateur exécute `nix flake check`, **Then** la commande réussit sans erreur après avoir vérifié la construction du paquet (incluant `pytest`) et l'évaluation du module `nixosModules.default`.

---

### User Story 4 - Documentation complète d'intégration Homelab NixOS, n8n et WAHA (`README.md`) (Priority: P2)

Un administrateur ou bénévole consultant le fichier `README.md` dispose d'instructions claires en français expliquant :
- l'utilisation des nouvelles commandes packagées (`sgdf-extract`, `sgdf-vcf`, `sgdf-api`, `nix build`, `nix run .#sgdf-api`, `nix build .#oci-image`),
- l'intégration déclarative du flake dans le `flake.nix` d'un serveur NixOS (activation de `services.sgdf-utils` et gestion du secret `SGDF_API_KEY` via `sops-nix` ou `agenix`),
- des exemples concrets de configuration de workflows **n8n** et **WAHA** (import d'`ExportIndividus.xls`, diffusion WhatsApp par unité via `/api/v1/units/{unit_name}/whatsapp-recipients`, identification d'un parent sur message entrant via `/api/v1/parents/by-phone/{phone}` et mise à jour de `has_whatsapp`).

**Why this priority**: Permet une mise en œuvre immédiate sur le homelab sans avoir à deviner la syntaxe des options NixOS ou des requêtes HTTP entre n8n, WAHA et `sgdf-utils`.

**Independent Test**: Peut être vérifié en relisant le `README.md` et en contrôlant que tous les exemples de commandes, de configuration NixOS et d'appels n8n/WAHA correspondent exactement aux options et routes implémentées.

**Acceptance Scenarios**:

1. **Given** le fichier `README.md`, **When** un administrateur suit la section de déploiement NixOS, **Then** il trouve un exemple complet d'ajout de l'entrée `sgdf-utils` dans `inputs`, d'import de `nixosModules.default` et de configuration de `services.sgdf-utils` avec `environmentFile`.
2. **Given** le fichier `README.md`, **When** un administrateur configure ses automatisations, **Then** il trouve des exemples précis d'interconnexion entre **n8n**, **WAHA** et l'API `sgdf-utils` (en-tête `X-API-Key`, import intranet, diffusion par unité et webhook de réception WhatsApp).

---

### Edge Cases

- **Exécution de `sgdf-extract` et `sgdf-vcf` en tant que scripts installés vs scripts à la racine** : Les commandes `sgdf-extract` et `sgdf-vcf` déclarées dans `pyproject.toml` doivent fonctionner identiquement aux scripts `extract_parent_contacts.py` et `generate_contacts_vcf.py` présents à la racine du dépôt, sans casser les imports existants dans la suite de tests.
- **Personnalisation de `services.sgdf-utils.dataDir`** : Si `dataDir` est fixé au chemin par défaut `"/var/lib/sgdf-utils"`, `StateDirectory = "sgdf-utils"` gère automatiquement la création et les permissions du dossier ; si l'administrateur spécifie un chemin `dataDir` personnalisé en dehors de `/var/lib/sgdf-utils`, le module configure `SGDF_DATABASE_URL = "sqlite:///${cfg.dataDir}/sgdf.sqlite3"` et accorde l'accès en écriture (`ReadWritePaths`) au répertoire cible.
- **Construction dans le bac à sable Nix (`checkPhase`)** : Pendant `nix build`, le bac à sable Nix n'a aucun accès réseau et le répertoire source peut être en lecture seule ; tous les tests `pytest` doivent s'exécuter avec succès dans ce bac à sable en utilisant uniquement des répertoires temporaires (`tmp_path`) ou la mémoire vive.
- **Option `environmentFile` non renseignée (`null`)** : Lorsque `services.sgdf-utils.environmentFile` vaut `null` (valeur par défaut), aucune directive `EnvironmentFile` n'est injectée dans l'unité `systemd` et le service démarre normalement sur l'interface locale (`127.0.0.1`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le dépôt DOIT inclure un fichier `pyproject.toml` standard déclarant le paquet Python `sgdf-contacts`, ses métadonnées, ses dépendances d'exécution et trois scripts exécutables (`[project.scripts]`) :
  - `sgdf-extract` (CLI d'extraction Excel),
  - `sgdf-vcf` (CLI de génération vCard),
  - `sgdf-api` (lancement du serveur HTTP REST FastAPI/Uvicorn).
- **FR-002**: Les scripts historiques `extract_parent_contacts.py` et `generate_contacts_vcf.py` à la racine du dépôt DOIVENT rester fonctionnels et rétrocompatibles tout en partageant leurs points d'entrée avec `sgdf-extract` et `sgdf-vcf`.
- **FR-003**: Le fichier `flake.nix` DOIT exposer `packages.<system>.default` (et `packages.<system>.sgdf-contacts`) construit via `pkgs.python3Packages.buildPythonApplication` à partir de `pyproject.toml`, en exécutant la suite de tests `pytest` dans `checkPhase` (`nativeCheckInputs`).
- **FR-004**: Le fichier `flake.nix` DOIT permettre de lancer directement le serveur API via `nix run .#sgdf-api` (ainsi que `nix run` par défaut ou via `apps.<system>.sgdf-api`, `apps.<system>.sgdf-extract` et `apps.<system>.sgdf-vcf`).
- **FR-005**: Sur les systèmes Linux (`x86_64-linux`, `aarch64-linux`), le fichier `flake.nix` DOIT exposer `packages.<system>.oci-image` construit via `pkgs.dockerTools.buildLayeredImage`, embarquant le paquet `sgdf-contacts`, configurant `sgdf-api` comme commande de démarrage, utilisant `SGDF_HOST=0.0.0.0`, `SGDF_PORT=8000` et `SGDF_DATABASE_URL=sqlite:////data/sgdf.sqlite3` par défaut, et exposant le port `8000`.
- **FR-006**: Le fichier `flake.nix` DOIT exposer `nixosModules.default` (et `nixosModules.sgdf-utils`) déclarant les options `services.sgdf-utils` suivantes :
  - `enable` (`bool`, défaut `false`),
  - `package` (paquet à utiliser, défaut : le paquet `sgdf-contacts` du flake pour le système cible),
  - `host` (`str`, défaut `"127.0.0.1"`),
  - `port` (`port`, défaut `8000`),
  - `dataDir` (`path` ou `str`, défaut `"/var/lib/sgdf-utils"`),
  - `environmentFile` (`nullOr path`, défaut `null`, chemin vers le fichier de secrets géré par `sops-nix` ou `agenix` contenant notamment `SGDF_API_KEY`).
- **FR-007**: Lorsque `services.sgdf-utils.enable = true`, le module NixOS DOIT déclarer un service `systemd.services.sgdf-utils` démarrant après `network.target`, configurant `SGDF_HOST`, `SGDF_PORT` et `SGDF_DATABASE_URL = "sqlite:///${cfg.dataDir}/sgdf.sqlite3"`, chargeant `EnvironmentFile` si `environmentFile != null`, et appliquant le durcissement `systemd` suivant :
  - `DynamicUser = true`,
  - `StateDirectory = "sgdf-utils"`,
  - `WorkingDirectory = cfg.dataDir`,
  - `ProtectSystem = "strict"`,
  - `ProtectHome = true`,
  - `PrivateTmp = true`,
  - `NoNewPrivileges = true`.
- **FR-008**: Le fichier `flake.nix` DOIT définir des vérifications dans `checks.<system>` permettant à `nix flake check` de valider la construction du paquet Python (avec `pytest`) ainsi que l'évaluation du module NixOS `nixosModules.default` et des options `services.sgdf-utils`.
- **FR-009**: Le fichier `README.md` DOIT documenter en français :
  - l'utilisation des commandes packagées (`nix build`, `nix run .#sgdf-api`, `nix build .#oci-image`, `sgdf-extract`, `sgdf-vcf`, `sgdf-api`),
  - l'intégration déclarative de `nixosModules.default` et `services.sgdf-utils` dans le `flake.nix` d'un homelab NixOS (avec `sops-nix` / `agenix`),
  - des exemples concrets de configuration de nœuds **n8n** et **WAHA** interagissant avec l'API.
- **FR-010**: Conformément à la constitution du projet, l'intégralité des identifiants de code source Python et Nix internes DOIT être en anglais, tandis que les descriptions d'options, commentaires, docstrings et la documentation (`README.md`) DOIVENT être rédigés en français.

### Key Entities

- **Paquet Applicatif (`sgdf-contacts`)** : Distribution Python standardisée par `pyproject.toml` et construite de manière reproductible par Nix, regroupant le module `sgdf_contacts` et les trois exécutables CLI (`sgdf-extract`, `sgdf-vcf`, `sgdf-api`).
- **Module NixOS (`services.sgdf-utils`)** : Interface de configuration déclarative permettant d'activer, paramétrer et isoler le service `sgdf-api` sous forme d'unité `systemd` durcie sur un hôte NixOS, avec persistance automatique dans `/var/lib/sgdf-utils/sgdf.sqlite3`.
- **Image Conteneur OCI (`packages.oci-image`)** : Image conteneur minimale en couches générée par Nix pour exécuter `sgdf-api` dans un environnement Podman ou Docker.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `nix build` construit le paquet `sgdf-contacts` de bout en bout et exécute 100 % de la suite de tests `pytest` avec succès dans le bac à sable Nix.
- **SC-002**: Les trois commandes `sgdf-extract`, `sgdf-vcf` et `sgdf-api` sont présentes dans `./result/bin/` et `nix run .#sgdf-api` démarre le serveur FastAPI fonctionnel (répondant `200 OK` sur `GET /health`).
- **SC-003**: `nix flake check` s'exécute sans aucune erreur et valide à la fois le paquet, l'image OCI (sur Linux) et l'évaluation du module NixOS `nixosModules.default` (y compris ses directives de durcissement `systemd` et ses valeurs par défaut).
- **SC-004**: Le fichier `README.md` fournit une documentation complète en français couvrant le packaging Nix, le déploiement via `services.sgdf-utils` sur un homelab NixOS et l'interconnexion avec n8n et WAHA.

## Assumptions

- Les points d'entrée console `sgdf-extract` et `sgdf-vcf` exposés par `pyproject.toml` délèguent vers des fonctions situées dans `sgdf_contacts/entrypoints/` (tout en conservant `extract_parent_contacts.py` et `generate_contacts_vcf.py` à la racine comme façades rétrocompatibles) afin que tous les exécutables soient autonomes une fois le paquet `sgdf_contacts` installé dans le magasin Nix.
- Le fichier de base de données SQLite géré par le module NixOS est stocké sous `${cfg.dataDir}/sgdf.sqlite3` (soit `/var/lib/sgdf-utils/sgdf.sqlite3` par défaut), conformément au cahier des charges de l'issue #6.
- L'environnement de développement éphémère existant (`devShells.default` dans `flake.nix` et `devbox.json` activés par `direnv`) est intégralement préservé et enrichi de l'outil de packaging `setuptools` si nécessaire.
