# Implementation Plan: Empaquetage de l'Application et Module de Déploiement Déclaratif pour Serveur Domestique

**Branch**: `010-packager-flake-module-nixos` | **Date**: 2026-10-27 | **Spec**: [specs/010-packager-flake-module-nixos/spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-packager-flake-module-nixos/spec.md`

## Summary

Packager proprement l'application Python `sgdf-contacts` avec Nix (`pyproject.toml` + `buildPythonApplication`), exposer une image conteneur OCI optionnelle (`dockerTools.buildLayeredImage`), fournir un module NixOS déclaratif et durci (`nixosModules.default` / `services.sgdf-utils`) et documenter le déploiement sur le homelab NixOS aux côtés de **n8n** et **WAHA** :
1. Créer `pyproject.toml` déclarant le paquet `sgdf-contacts` et ses trois exécutables CLI (`sgdf-extract`, `sgdf-vcf`, `sgdf-api`), et structurer `sgdf_contacts/entrypoints/cli_extract.py` et `sgdf_contacts/entrypoints/cli_vcf.py` tout en maintenant la rétrocompatibilité totale de `extract_parent_contacts.py` et `generate_contacts_vcf.py`.
2. Faire évoluer `flake.nix` pour exposer `packages.default` (`buildPythonApplication` avec exécution de `pytest` dans `checkPhase`), `packages.oci-image` (`dockerTools.buildLayeredImage` sur Linux), `apps.sgdf-api` (`nix run .#sgdf-api`), `nixosModules.default` (`services.sgdf-utils.{enable, package, host, port, dataDir, environmentFile}` avec durcissement `systemd` complet) et `checks` pour `nix flake check`.
3. Enrichir `README.md` avec une documentation complète en français couvrant le packaging Nix, le déploiement déclaratif sur un homelab NixOS (`sops-nix` / `agenix`) et des exemples d'interconnexion avec **n8n** et **WAHA**.

## Technical Context

**Language/Version**: Python 3.14 + Nix (Flakes & module NixOS)

**Primary Dependencies**: `setuptools` (build-system PEP 621), `pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `sqlmodel`, `sqlalchemy`, `fastapi`, `uvicorn`, `python-multipart`, `httpx`, `pytest` (`pytestCheckHook`) et `ruff`

**Storage**: Base SQLite locale gérée automatiquement par `systemd` via `StateDirectory = "sgdf-utils"` dans `/var/lib/sgdf-utils/sgdf.sqlite3` (`SGDF_DATABASE_URL = "sqlite:///${cfg.dataDir}/sgdf.sqlite3"`)

**Testing**: `pytest` (incluant des tests dédiés pour `pyproject.toml` et les points d'entrée CLI `sgdf-extract`, `sgdf-vcf`, `sgdf-api`), `nix build` (`checkPhase` dans le bac à sable Nix), `nix flake check` (évaluation du paquet et du module NixOS `nixosModules.default`) et `ruff check .`

**Target Platform**: Homelab NixOS (`x86_64-linux`, `aarch64-linux`) et environnements de développement Linux / macOS

**Project Type**: Paquet applicatif Python (`pyproject.toml` + `buildPythonApplication`) + Module NixOS (`nixosModules.default`) + Image OCI (`dockerTools.buildLayeredImage`)

**Performance Goals**: Construction et vérification du flake reproductibles ; démarrage du service `sgdf-utils.service` en moins de 2 secondes sur NixOS

**Constraints**: Identifiants de code en anglais et commentaires, docstrings, descriptions d'options et documentation (`README.md`) en français (Principe I, constitution v2.1.0) ; préservation de l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv` (Principe II) ; gestion des secrets hors du `/nix/store` via `environmentFile` et durcissement `systemd` strict (Principe IV) ; simplicité et lisibilité du module NixOS (Principe V — YAGNI) ; travail sur branche dédiée `010-packager-flake-module-nixos`, messages de commit en anglais (consigne utilisateur) et ouverture d'une Pull Request dédiée via `gh` sans auto-fusion (Principe VI)

**Scale/Scope**: 1 fichier `pyproject.toml`, 3 exécutables CLI (`sgdf-extract`, `sgdf-vcf`, `sgdf-api`), 1 module NixOS déclaratif (`services.sgdf-utils`), 1 image OCI et documentation d'intégration homelab n8n/WAHA

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution (v2.1.0) | Statut | Justification de conformité |
| -------------------------------------- | -------- | ----------------------------- |
| **I. Code en Anglais et Documentation en Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Tous les identifiants Python et Nix internes sont en anglais. Les commentaires, docstrings, messages d'aide CLI, descriptions d'options NixOS et la documentation `README.md` sont en français. (Note : les messages de commit Git seront rédigés en anglais conformément à la consigne explicite de l'utilisateur). |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | `devShells.default` dans `flake.nix` et `devbox.json` restent en parité stricte et activés automatiquement par `direnv` via `.envrc`. |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Les 3 exécutables `sgdf-extract`, `sgdf-vcf` et `sgdf-api` sont exposés proprement via `pyproject.toml` et `sgdf_contacts/entrypoints/`, tout en conservant `extract_parent_contacts.py` et `generate_contacts_vcf.py` fonctionnels. |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | Le service NixOS isole les données dans `/var/lib/sgdf-utils/sgdf.sqlite3` avec `DynamicUser = true`, `ProtectSystem = "strict"`, `ProtectHome = true`, `PrivateTmp = true`, `NoNewPrivileges = true`, et charge `SGDF_API_KEY` via `environmentFile` sans jamais l'exposer dans `/nix/store`. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | `pyproject.toml` standard et module NixOS concis directement intégré dans `flake.nix` (et structuré proprement sous `nix/` si nécessaire) sans dépendance externe superflue. |
| **VI. Flux Git par Branche Dédiée et Pull Request (Squash and Merge)** | ✅ CONFORME | Travail effectué sur la branche dédiée `010-packager-flake-module-nixos` et création d'une Pull Request dédiée via `gh pr create` sans approbation ni fusion automatique. |

## Project Structure

### Documentation (this feature)

```text
specs/010-packager-flake-module-nixos/
├── plan.md                                       # Ce fichier (/speckit.plan)
├── research.md                                   # Décisions techniques Phase 0
├── data-model.md                                 # Schéma des options NixOS et métadonnées de packaging Phase 1
├── quickstart.md                                 # Guide de validation de bout en bout Phase 1
├── contracts/                                    # Contrats d'interface Phase 1
│   └── contrat-flake-et-module-nixos.md          # Contrat des sorties flake.nix, exécutables CLI et module NixOS
└── tasks.md                                      # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
pyproject.toml                                    # Nouveau : déclaration PEP 621 de sgdf-contacts et [project.scripts] (sgdf-extract, sgdf-vcf, sgdf-api)
flake.nix                                         # Évolution : packages.default (buildPythonApplication + pytest), packages.oci-image, apps.sgdf-api, nixosModules.default, checks
extract_parent_contacts.py                        # Conservé (façade rétrocompatible ré-exportant sgdf_contacts.entrypoints.cli_extract)
generate_contacts_vcf.py                          # Conservé (façade rétrocompatible ré-exportant sgdf_contacts.entrypoints.cli_vcf)
sgdf_contacts/
├── __init__.py                                   # Export public enrichi
├── domain/                                       # Inchangé
├── parsers/                                      # Inchangé
├── exporters/                                    # Inchangé
├── persistence/                                  # Inchangé
└── entrypoints/
    ├── __init__.py                               # Export des points d'entrée CLI et API
    ├── api.py                                    # Point d'entrée sgdf-api (run_server)
    ├── cli_extract.py                            # Nouveau : point d'entrée sgdf-extract
    └── cli_vcf.py                                # Nouveau : point d'entrée sgdf-vcf
README.md                                         # Mis à jour : documentation du packaging Nix, déploiement NixOS (services.sgdf-utils, sops-nix/agenix) et workflows n8n / WAHA
tests/
├── test_environment.py                           # Enrichi avec la vérification de pyproject.toml, flake.nix (packages, nixosModules) et des points d'entrée CLI
├── test_extract_parent_contacts.py               # Conservé
├── test_generate_contacts_vcf.py                 # Conservé
├── test_sgdf_contacts_package.py                 # Conservé
├── test_persistence.py                           # Conservé
└── test_api.py                                   # Conservé
```

**Structure Decision**: Ajout de `pyproject.toml` à la racine, regroupement propre des trois points d'entrée exécutables dans `sgdf_contacts/entrypoints/` (`cli_extract.py`, `cli_vcf.py`, `api.py`) avec maintien des scripts historiques à la racine, et enrichissement de `flake.nix` avec `packages`, `apps`, `nixosModules` et `checks`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution.
