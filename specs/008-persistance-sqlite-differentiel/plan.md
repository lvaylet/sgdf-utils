# Implementation Plan: Persistance Locale des Contacts Parents et Calcul de Différentiel d'Import

**Branch**: `008-persistance-sqlite-differentiel` | **Date**: 2026-10-26 | **Spec**: [specs/008-persistance-sqlite-differentiel/spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-persistance-sqlite-differentiel/spec.md`

## Summary

Ajouter au package `sgdf_contacts` un sous-package de persistance locale (`sgdf_contacts/persistence/`) basé sur **SQLite** (en mode WAL avec clés étrangères activées, compatible PostgreSQL via **SQLModel** et **SQLAlchemy**) afin de :
1. Déclarer `sqlmodel` et `sqlalchemy` en parité stricte dans `flake.nix` et `devbox.json` et exclure les fichiers de bases locales (`*.db`, `*.sqlite`, `*.sqlite3`, `*-wal`, `*-shm`) dans `.gitignore`.
2. Définir le schéma relationnel (`sgdf_contacts/persistence/models.py`) avec les trois tables `parents` (`ParentRecord`), `children` (`ChildRecord`) et `parent_child_links` (`ParentChildLink`), ainsi que l'activation automatique de `PRAGMA journal_mode=WAL;` et `PRAGMA foreign_keys=ON;` à chaque connexion SQLite.
3. Implémenter le dépôt transactionnel et le calcul de différentiel (`sgdf_contacts/persistence/repository.py` : `ParentContactRepository`, `ImportDiffReport`, `ParentUpdateDiff`, `FieldChange`) avec réconciliation par `member_id` ou `(last_name, first_name)`, désactivation douce (`is_active = False` sans perte de `has_whatsapp`), requêtage/filtrage avancé et régénération directe de `ContactParents.vcf` et `ContactsParents.xlsx` depuis la base SQLite.

## Technical Context

**Language/Version**: Python 3.14 (fourni par l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv`)

**Primary Dependencies**: `sqlmodel` (0.0.42), `sqlalchemy` (2.0.51), `beautifulsoup4`, `lxml`, `openpyxl`, bibliothèque standard Python (`dataclasses`, `datetime`, `io`, `pathlib`, `typing`), `pytest` et `ruff`

**Storage**: Base SQLite locale (en mode WAL avec `foreign_keys=ON`, fichier `.db` ou `:memory:` en test, exclue de Git via `.gitignore`) + fichiers d'entrée/sortie (`ExportIndividus.xls` en lecture seule, `ContactsParents.xlsx`, `ContactParents.vcf`)

**Testing**: `pytest` (tests existants + `tests/test_persistence.py` couvrant le schéma, les pragmas SQLite, l'import idempotent, le calcul de différentiel `ImportDiffReport`, le requêtage/filtrage et la régénération `.vcf`/`.xlsx` depuis SQLite) et `ruff check .`

**Target Platform**: Environnement éphémère Linux / macOS activé par `direnv`

**Project Type**: Package Python modulaire (`sgdf_contacts/`) + scripts CLI d'automatisation Python 3 à la racine

**Performance Goals**: Import complet et calcul de différentiel des 134 parents et de leurs enfants en moins de 1 seconde sur SQLite local

**Constraints**: Identifiants de code en anglais et commentaires, docstrings, messages utilisateur et documentation (`README.md`) en français (Principe I, constitution v2.1.0) ; déclaration des dépendances dans `flake.nix` et `devbox.json` en parité stricte (Principe II) ; lecture seule des fichiers sources et exclusion des fichiers `.db` dans `.gitignore` (Principe IV) ; simplicité sans migration complexe inutile (Principe V — YAGNI) ; travail sur branche dédiée `008-persistance-sqlite-differentiel` et ouverture d'une Pull Request via `gh` avec un titre en anglais (Principe VI + consigne utilisateur)

**Scale/Scope**: 153 lignes dans `ExportIndividus.xls` → 134 parents uniques et leurs enfants stockés dans SQLite (`parents`, `children`, `parent_child_links`) → régénération fidèle des 134 fiches dans `ContactParents.vcf` et `ContactsParents.xlsx`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution (v2.1.0) | Statut | Justification de conformité |
| -------------------------------------- | -------- | ----------------------------- |
| **I. Code en Anglais et Documentation en Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Tous les noms de modules (`persistence`, `models`, `repository`), classes (`ParentRecord`, `ChildRecord`, `ParentChildLink`, `ParentContactRepository`, `ImportDiffReport`, `ParentUpdateDiff`, `FieldChange`), méthodes et colonnes sont en anglais (PEP 8). Tous les commentaires, docstrings et la mise à jour de `README.md` sont en français. |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | `sqlmodel` et `sqlalchemy` sont déclarés à l'identique dans `flake.nix` et `devbox.json` et vérifiés par `tests/test_environment.py`. |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Le sous-package `sgdf_contacts/persistence/` s'intègre proprement dans l'architecture modulaire existante sans casser les scripts CLI existants. |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | Les bases SQLite locales (`*.db`, `*.sqlite*`, `*-wal`, `*-shm`) sont exclues via `.gitignore` afin qu'aucune base contenant des données personnelles ne puisse être commise. `ExportIndividus.xls` reste lu strictement en lecture seule. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | Utilisation directe de `SQLModel` / `SQLAlchemy` avec initialisation de schéma déclarative (`SQLModel.metadata.create_all`) sans surcouche inutile. |
| **VI. Flux Git par Branche Dédiée et Pull Request (Squash and Merge)** | ✅ CONFORME | Travail réalisé sur la branche dédiée `008-persistance-sqlite-differentiel` et soumission via `gh pr create` avec un titre en anglais sans auto-fusion. |

## Project Structure

### Documentation (this feature)

```text
specs/008-persistance-sqlite-differentiel/
├── plan.md                                  # Ce fichier (/speckit.plan)
├── research.md                              # Décisions techniques Phase 0
├── data-model.md                            # Modèle de données SQLModel et rapport de différentiel Phase 1
├── quickstart.md                            # Guide de validation de bout en bout Phase 1
├── contracts/                               # Contrats d'interface Phase 1
│   └── contrat-persistance.md               # Contrat de l'API publique sgdf_contacts.persistence
└── tasks.md                                 # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
flake.nix                                    # Ajout de sqlmodel et sqlalchemy dans python3.withPackages
devbox.json                                  # Ajout de python3Packages.sqlmodel@latest et python3Packages.sqlalchemy@latest en parité
.gitignore                                   # Exclusion des bases SQLite locales (*.db, *.sqlite, *.sqlite3, *-wal, *-shm)
sgdf_contacts/
├── __init__.py                              # Ré-export des classes et fonctions de persistance
├── domain/                                  # Inchangé (zéro dépendance externe)
├── parsers/                                 # Inchangé
├── exporters/                               # Inchangé
└── persistence/
    ├── __init__.py                          # Export public du sous-package persistence
    ├── models.py                            # Modèles SQLModel (ParentRecord, ChildRecord, ParentChildLink) + create_db_engine (WAL + FK) + init_db
    └── repository.py                        # ParentContactRepository, ImportDiffReport, ParentUpdateDiff, FieldChange, requêtage et régénération VCF/Excel
README.md                                    # Documentation mise à jour en français pour présenter la persistance SQLite et le calcul de différentiel
tests/
├── test_environment.py                      # Mis à jour avec sqlmodel/sqlalchemy et motifs .db dans .gitignore
├── test_extract_parent_contacts.py          # Conservé
├── test_generate_contacts_vcf.py            # Conservé
├── test_sgdf_contacts_package.py            # Conservé
└── test_persistence.py                      # Nouveau : tests unitaires et d'intégration SQLite (WAL, FK, upsert, idempotence, diff, filtres, recherche téléphone, régénération VCF/XLSX)
```

**Structure Decision**: Ajout du sous-package `sgdf_contacts/persistence/` (`__init__.py`, `models.py`, `repository.py`) à côté de `domain/`, `parsers/` et `exporters/`, mise à jour déclarative de `flake.nix`, `devbox.json` et `.gitignore`, et ajout de la suite de tests `tests/test_persistence.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution.
