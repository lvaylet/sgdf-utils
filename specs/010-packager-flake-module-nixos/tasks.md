---

description: "Task list for packaging the application in flake.nix and creating the NixOS module"
---

# Tasks: Empaquetage de l'Application et Module de Déploiement Déclaratif pour Serveur Domestique

**Input**: Design documents from `/specs/010-packager-flake-module-nixos/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/contrat-flake-et-module-nixos.md, quickstart.md

**Tests**: Inclus conformément aux critères d'acceptation de l'issue #6 et à la spécification (`tests/test_environment.py`, `pytest` dans `checkPhase` via `nix build`, et `nix flake check` évaluant `nixosModules.default`).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Package, CLI, Nix & Docs**: `pyproject.toml`, `flake.nix`, `sgdf_contacts/entrypoints/`, `extract_parent_contacts.py`, `generate_contacts_vcf.py`, `tests/`, `README.md` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialisation du fichier de packaging standard `pyproject.toml` et mise à jour de `.gitignore` pour les artefacts de construction Python et Nix.

- [X] T001 Créer `pyproject.toml` à la racine du dépôt déclarant `build-system` (`setuptools>=61.0`, `setuptools.build_meta`), les métadonnées `[project]` (`name = "sgdf-contacts"`, `version = "1.0.0"`, `requires-python = ">=3.10"`, dépendances d'exécution), les scripts `[project.scripts]` (`sgdf-extract = "sgdf_contacts.entrypoints.cli_extract:main"`, `sgdf-vcf = "sgdf_contacts.entrypoints.cli_vcf:main"`, `sgdf-api = "sgdf_contacts.entrypoints.api:run_server"`) et la découverte des paquets/modules `[tool.setuptools]`
- [X] T002 [P] Mettre à jour `.gitignore` pour ignorer les liens de résultat Nix (`result`, `result-*`) et les artefacts de packaging Python (`build/`, `dist/`, `*.egg-info/`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Centralisation des points d'entrée CLI d'extraction Excel et de génération vCard dans `sgdf_contacts/entrypoints/` tout en préservant à 100 % la rétrocompatibilité des scripts historiques `extract_parent_contacts.py` et `generate_contacts_vcf.py`.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Créer `sgdf_contacts/entrypoints/cli_extract.py` implémentant `run_extraction(input_path: Path, output_path: Path) -> list[ParentContact]`, `parse_args(argv: list[str] | None = None) -> argparse.Namespace` et `main(argv: list[str] | None = None) -> int` pour la commande `sgdf-extract`, et mettre à jour `extract_parent_contacts.py` pour déléguer et ré-exporter tous les symboles sans régression
- [X] T004 [P] Créer `sgdf_contacts/entrypoints/cli_vcf.py` implémentant `run_vcf_generation(input_path: Path, output_path: Path) -> list[ParentContactCard]`, `parse_args(argv: list[str] | None = None) -> argparse.Namespace` et `main(argv: list[str] | None = None) -> int` pour la commande `sgdf-vcf`, et mettre à jour `generate_contacts_vcf.py` pour déléguer et ré-exporter tous les symboles sans régression
- [X] T005 Mettre à jour `sgdf_contacts/entrypoints/__init__.py` et `sgdf_contacts/__init__.py` pour exposer `run_server` ainsi que les points d'entrée CLI `cli_extract` et `cli_vcf`

**Checkpoint**: Les trois points d'entrée (`cli_extract:main`, `cli_vcf:main`, `api:run_server`) sont prêts dans `sgdf_contacts.entrypoints` et rétrocompatibles avec toute la suite de tests existante.

---

## Phase 3: User Story 1 - Empaquetage standard de l'application et exécution directe des commandes (`sgdf-extract`, `sgdf-vcf`, `sgdf-api`) (Priority: P1) 🎯 MVP

**Goal**: Construire le paquet Python `sgdf-contacts` via `pkgs.python3Packages.buildPythonApplication` dans `flake.nix` (avec exécution de `pytest` dans `checkPhase`), exposer les trois exécutables `sgdf-extract`, `sgdf-vcf` et `sgdf-api` dans `result/bin/`, et permettre l'exécution directe du serveur API via `nix run .#sgdf-api`.

**Independent Test**: Exécuter `nix build` (qui doit réussir la `checkPhase` `pytest`), vérifier `./result/bin/sgdf-extract --help` et `./result/bin/sgdf-vcf --help`, et tester `nix run .#sgdf-api` avec une requête `GET /health`.

### Implementation for User Story 1

- [X] T006 [US1] Mettre à jour `flake.nix` pour définir `packages.<system>.default` et `packages.<system>.sgdf-contacts` via `pkgs.python3Packages.buildPythonApplication` (`pname = "sgdf-contacts"`, `version = "1.0.0"`, `pyproject = true`, `build-system = [ pkgs.python3Packages.setuptools ]`, `dependencies` complètes, `nativeCheckInputs = [ pkgs.python3Packages.pytestCheckHook pkgs.ruff ]`, `meta.mainProgram = "sgdf-api"`) ainsi que `apps.<system>.{default, sgdf-api, sgdf-extract, sgdf-vcf}`
- [X] T007 [US1] Enrichir `tests/test_environment.py` avec des tests vérifiant la présence et la validité de `pyproject.toml`, la déclaration des trois scripts `sgdf-extract`, `sgdf-vcf` et `sgdf-api`, et le fonctionnement des points d'entrée `sgdf_contacts.entrypoints.cli_extract:main`, `sgdf_contacts.entrypoints.cli_vcf:main` et `sgdf_contacts.entrypoints.api:run_server`

**Checkpoint**: User Story 1 est fonctionnelle et testable indépendamment via `pytest`, `nix build` et `nix run .#sgdf-api`.

---

## Phase 4: User Story 2 - Déploiement déclaratif et durci du service sur un serveur NixOS (`nixosModules.default`) (Priority: P1)

**Goal**: Exposer `nixosModules.default` (et `nixosModules.sgdf-utils`) dans `flake.nix` déclarant les options `services.sgdf-utils` (`enable`, `package`, `host` défaut `"127.0.0.1"`, `port` défaut `8000`, `dataDir` défaut `"/var/lib/sgdf-utils"`, `environmentFile` défaut `null`) et configurant le service `systemd.services.sgdf-utils` durci (`DynamicUser = true`, `StateDirectory = "sgdf-utils"`, `ProtectSystem = "strict"`, `ProtectHome = true`, `PrivateTmp = true`, `NoNewPrivileges = true`).

**Independent Test**: Évaluer une configuration NixOS important `nixosModules.default` avec `services.sgdf-utils.enable = true` et vérifier que `systemd.services.sgdf-utils` possède toutes les variables d'environnement (`SGDF_HOST`, `SGDF_PORT`, `SGDF_DATABASE_URL = "sqlite:////var/lib/sgdf-utils/sgdf.sqlite3"`), `EnvironmentFile` et les directives de durcissement `systemd` requises.

### Implementation for User Story 2

- [X] T008 [US2] Implémenter `nixosModules.default` (et `nixosModules.sgdf-utils`) dans `flake.nix` déclarant `options.services.sgdf-utils` (`enable: bool = false`, `package: package`, `host: str = "127.0.0.1"`, `port: port = 8000`, `dataDir: str = "/var/lib/sgdf-utils"`, `environmentFile: nullOr path = null`) et générant `systemd.services.sgdf-utils` avec `SGDF_HOST`, `SGDF_PORT`, `SGDF_DATABASE_URL = "sqlite:///${cfg.dataDir}/sgdf.sqlite3"`, `EnvironmentFile` conditionnel et les directives `DynamicUser = true`, `StateDirectory = "sgdf-utils"`, `WorkingDirectory = cfg.dataDir`, `ProtectSystem = "strict"`, `ProtectHome = true`, `PrivateTmp = true` et `NoNewPrivileges = true`
- [X] T009 [US2] Ajouter dans `tests/test_environment.py` un test vérifiant que `flake.nix` expose `nixosModules.default`, les options `services.sgdf-utils` (`enable`, `host`, `port`, `dataDir`, `environmentFile`) et les directives de durcissement `systemd` (`DynamicUser`, `StateDirectory`, `ProtectSystem`, `ProtectHome`, `PrivateTmp`, `NoNewPrivileges`)

**Checkpoint**: Le module NixOS `nixosModules.default` est complet et vérifié.

---

## Phase 5: User Story 3 - Construction d'image conteneur OCI et validation globale du Flake (`packages.oci-image` & `nix flake check`) (Priority: P2)

**Goal**: Exposer `packages.<system>.oci-image` (`pkgs.dockerTools.buildLayeredImage` sur Linux) et configurer `checks.<system>` dans `flake.nix` afin que `nix flake check` valide le paquet Python, l'image OCI et l'évaluation complète d'un système NixOS utilisant `nixosModules.default`.

**Independent Test**: Exécuter `nix build .#oci-image` et `nix flake check` et vérifier qu'ils se terminent tous deux avec un code de retour `0`.

### Implementation for User Story 3

- [X] T010 [US3] Ajouter `packages.<system>.oci-image` (`pkgs.dockerTools.buildLayeredImage` sur Linux exécutant `sgdf-api` sur `0.0.0.0:8000` avec `SGDF_DATABASE_URL=sqlite:////data/sgdf.sqlite3`) et `checks.<system>` (`package`, `oci-image` et `nixos-module` évaluant `nixpkgs.lib.nixosSystem` avec `self.nixosModules.default` et vérifiant par assertions les options et le durcissement de `systemd.services.sgdf-utils`) dans `flake.nix`

**Checkpoint**: `nix build .#oci-image` et `nix flake check` passent sans erreur.

---

## Phase 6: User Story 4 - Documentation complète d'intégration Homelab NixOS, n8n et WAHA (`README.md`) (Priority: P2)

**Goal**: Documenter en français dans `README.md` l'utilisation des commandes packagées (`sgdf-extract`, `sgdf-vcf`, `sgdf-api`, `nix build`, `nix run .#sgdf-api`, `nix build .#oci-image`), l'intégration de `nixosModules.default` / `services.sgdf-utils` dans le `flake.nix` d'un homelab NixOS (avec `sops-nix` ou `agenix`) et des exemples de workflows **n8n** et **WAHA**.

**Independent Test**: Vérifier que `README.md` couvre l'ensemble des commandes Nix, des options `services.sgdf-utils` et des scénarios d'interconnexion n8n / WAHA décrits dans `contracts/contrat-flake-et-module-nixos.md`.

### Implementation for User Story 4

- [X] T011 [US4] Mettre à jour `README.md` en français avec une section dédiée au packaging Nix (`pyproject.toml`, `nix build`, `nix run .#sgdf-api`, `nix build .#oci-image`, `nix flake check`), au déploiement déclaratif via `nixosModules.default` (`services.sgdf-utils`, `sops-nix` / `agenix`) et aux exemples de configuration de nœuds **n8n** et **WAHA**

**Checkpoint**: Toutes les User Stories (US1, US2, US3, US4) sont implémentées et documentées.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation finale de bout en bout (`pytest`, `ruff`, `nix build`, `nix run .#sgdf-api`, `nix build .#oci-image`, `nix flake check`), commits avec messages en anglais et création de la Pull Request dédiée via `gh`.

- [X] T012 Exécuter la validation complète de bout en bout (`pytest -v`, `ruff check .`, `nix build`, `nix run .#sgdf-api`, `nix build .#oci-image`, `nix flake check`) conformément à `specs/010-packager-flake-module-nixos/quickstart.md`
- [X] T013 Enregistrer les modifications sur la branche `010-packager-flake-module-nixos` avec des messages de commit en anglais, pousser la branche vers `origin` et ouvrir une Pull Request dédiée via `gh pr create` (sans l'approuver ni la fusionner)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1 : T001–T002)**: Aucune dépendance — démarre immédiatement. T001 et T002 sont parallélisables.
- **Foundational (Phase 2 : T003–T005)**: Dépend de la Phase 1 — bloque les User Stories. T003 et T004 sont parallélisables.
- **User Story 1 (Phase 3 : T006–T007)**: Dépend de la Phase 2.
- **User Story 2 (Phase 4 : T008–T009)**: Dépend de la Phase 3 (`nixosModules.default` utilise `packages.<system>.default` par défaut).
- **User Story 3 (Phase 5 : T010)**: Dépend des Phases 3 et 4 (`checks` valide à la fois `packages.default`, `packages.oci-image` et `nixosModules.default`).
- **User Story 4 (Phase 6 : T011)**: Peut s'exécuter en parallèle des Phases 4 et 5 dès que le contrat est fixé.
- **Polish (Phase 7 : T012–T013)**: Dépend de la complétion des Phases 3 à 6.

### Parallel Opportunities

- En Phase 1 : `T001` (`pyproject.toml`) et `T002` (`.gitignore`) portent sur des fichiers distincts.
- En Phase 2 : `T003` (`cli_extract.py` / `extract_parent_contacts.py`) et `T004` (`cli_vcf.py` / `generate_contacts_vcf.py`) portent sur des fichiers distincts et peuvent être exécutés en parallèle.
- En Phase 6 : `T011` (`README.md`) est indépendant du code dans `flake.nix` et `tests/test_environment.py`.

---

## Parallel Example: Foundational Phase

```bash
# Exécution parallèle de l'extraction des deux points d'entrée CLI dans sgdf_contacts/entrypoints/ :
Task T003: "Créer sgdf_contacts/entrypoints/cli_extract.py et mettre à jour extract_parent_contacts.py"
Task T004: "Créer sgdf_contacts/entrypoints/cli_vcf.py et mettre à jour generate_contacts_vcf.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Compléter Phase 1 (`pyproject.toml` + `.gitignore`) et Phase 2 (`sgdf_contacts/entrypoints/cli_extract.py` + `cli_vcf.py`).
2. Compléter Phase 3 (User Story 1 : `packages.default` avec `buildPythonApplication` + `pytest` et `apps.sgdf-api`).
3. **STOP & VALIDATE** : Vérifier `nix build` et `nix run .#sgdf-api`.

### Incremental Delivery

1. Setup + Foundational → `pyproject.toml` et points d'entrée CLI prêts.
2. User Story 1 → Paquet Nix `sgdf-contacts` construit et testé dans le bac à sable Nix, commandes `sgdf-extract`, `sgdf-vcf` et `sgdf-api` opérationnelles.
3. User Story 2 → Module NixOS déclaratif `nixosModules.default` (`services.sgdf-utils`) avec durcissement `systemd` complet.
4. User Story 3 → Image conteneur `packages.oci-image` et validation automatisée `nix flake check`.
5. User Story 4 & Polish → Documentation homelab `README.md` (NixOS + n8n + WAHA), vérifications finales, commits en anglais et ouverture de la Pull Request dédiée via `gh`.
