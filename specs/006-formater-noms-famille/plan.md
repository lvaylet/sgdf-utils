# Implementation Plan: Formatage des Noms de Famille en Casse Titre Comme les Prénoms

**Branch**: `006-formater-noms-famille` | **Date**: 2026-10-23 | **Spec**: [specs/006-formater-noms-famille/spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-formater-noms-famille/spec.md`

## Summary

Uniformiser le formatage des noms de famille sur celui des prénoms (en minuscules avec la première lettre de chaque mot ou segment délimité par un espace, un trait d'union `-` ou une apostrophe `'` en majuscule, ex. `Dupont`, `Dupont-Moretti`, `Le Goff`, `D'Artagnan`). Dans `extract_parent_contacts.py`, la fonction `normalize_last_name` applique désormais la même règle de casse titre que `normalize_first_name`, ce qui propage automatiquement ce formatage aux noms des parents (colonne `Nom`), aux noms des enfants (colonne `Noms des enfants` sous la forme `Prénom Nom`), à l'indexation des profils adultes et, par continuité, au fichier `ContactParents.vcf` généré par `generate_contacts_vcf.py` (`N`, `FN` au format `Prénom Nom` et `NOTE` avec `Enfants : Prénom Nom (Unité)`). Les docstrings, la documentation `README.md` et les suites de tests automatisés sont mis à jour en conséquence.

## Technical Context

**Language/Version**: Python 3.14 (fourni par l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv`)

**Primary Dependencies**: `beautifulsoup4`, `lxml`, `openpyxl`, bibliothèque standard Python (`argparse`, `dataclasses`, `pathlib`, `re`, `sys`, `unicodedata`, `zipfile`), `pytest` et `ruff`

**Storage**: Fichiers locaux (`ExportIndividus.xls` en lecture seule → `ContactsParents.xlsx` → `ContactParents.vcf`, tous exclus du suivi Git via `.gitignore`)

**Testing**: `pytest` (tests unitaires et d'intégration dans `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) et `ruff check .`

**Target Platform**: Environnement éphémère Linux / macOS activé par `direnv`

**Project Type**: Scripts CLI d'automatisation Python 3

**Performance Goals**: Exécution complète de l'extraction et de la génération `.vcf` en moins de 5 secondes pour un groupe scout standard (< 500 lignes)

**Constraints**: Identifiants de code en anglais et commentaires, docstrings, messages utilisateur et documentation (`README.md`) en français (Principe I, constitution v2.0.0) ; environnement éphémère Nix/Devbox sans dépendance supplémentaire (Principe II) ; lecture seule stricte des fichiers d'entrée et zéro donnée personnelle dans le code ou les tests (Principe IV) ; simplicité et réutilisation de la logique existante (Principe V — YAGNI)

**Scale/Scope**: 153 lignes dans `ExportIndividus.xls` → 134 parents uniques sur 13 colonnes dans l'onglet `ContactsParents` de `ContactsParents.xlsx` → 134 fiches `VCARD` dans `ContactParents.vcf`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution (v2.0.0) | Statut | Justification de conformité |
| -------------------------------------- | -------- | ----------------------------- |
| **I. Code en Anglais et Documentation en Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Les identifiants de code (`normalize_last_name`, `normalize_first_name`, etc.) restent en anglais selon PEP 8. Les docstrings, commentaires et le fichier `README.md` sont mis à jour en français (`Prénom Nom`). |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | Aucune nouvelle dépendance ; exécution et vérification au sein de l'environnement éphémère existant (`flake.nix` / `devbox.json` + `direnv`). |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Les scripts CLI `extract_parent_contacts.py` et `generate_contacts_vcf.py` conservent leur interface CLI, leurs messages en français et leurs codes de sortie standards. |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | Lecture seule stricte de `ExportIndividus.xls` (et de l'onglet brut `ExportIndividus`) ainsi que de `ContactsParents.xlsx`. Aucune donnée personnelle réelle dans le code ou les tests. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | `normalize_last_name` partage exactement la même règle simple par expression régulière que `normalize_first_name`, sans aucune dépendance ni abstraction supplémentaire. |

## Project Structure

### Documentation (this feature)

```text
specs/006-formater-noms-famille/
├── plan.md                                  # Ce fichier (/speckit.plan)
├── research.md                              # Décisions techniques Phase 0
├── data-model.md                            # Modèle de données et formatage des noms Phase 1
├── quickstart.md                            # Guide de validation de bout en bout Phase 1
├── contracts/                               # Contrats d'interface Phase 1
│   └── contrat-formatage-noms.md            # Contrat de formatage des noms dans Excel et vCard
└── tasks.md                                 # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
extract_parent_contacts.py                   # Mis à jour : normalize_last_name en casse titre et docstrings 'Prénom Nom'
generate_contacts_vcf.py                     # Mis à jour : docstrings 'Prénom Nom'
README.md                                    # Mis à jour : documentation du formatage des noms de famille et exemples 'Prénom Nom'
tests/
├── test_environment.py                      # Inchangé : tests de l'environnement éphémère
├── test_extract_parent_contacts.py          # Mis à jour : assertions de casse titre sur les noms des parents et enfants
└── test_generate_contacts_vcf.py            # Mis à jour : assertions 'Prénom Nom' dans N, FN et NOTE des vCard
```

**Structure Decision**: Modification ciblée en place de `extract_parent_contacts.py`, `generate_contacts_vcf.py`, `README.md` et des deux fichiers de tests unitaires et d'intégration dans `tests/`, sans ajout de nouveau fichier source.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution.
