# Implementation Plan: Extraction du Cœur Métier dans un Package Modulaire `sgdf_contacts`

**Branch**: `007-extraire-package-sgdf-contacts` | **Date**: 2026-10-26 | **Spec**: [specs/007-extraire-package-sgdf-contacts/spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-extraire-package-sgdf-contacts/spec.md`

## Summary

Extraire et structurer le cœur métier de `extract_parent_contacts.py` et `generate_contacts_vcf.py` dans un package Python modulaire `sgdf_contacts/` séparant trois sous-packages :
1. `sgdf_contacts/domain/` (zéro dépendance externe) : entités métier (`ParentContact` avec propriété `waha_chat_id`, `AttachedChild`, `AdultGroupProfile`, `ParentContactCard`), exceptions métier (`ContactExtractionError`, `VcfGenerationError`), constantes partagées (`PARENT_CONTACTS_HEADERS`, `ADULT_ROLE_LABELS`, `DEFAULT_CATEGORIES`, noms de feuilles et de fichiers par défaut) et fonctions pures de nettoyage, de normalisation et de tri alphabétique français.
2. `sgdf_contacts/parsers/` : lecture de `ExportIndividus.xls` (`read_individuals_export_table`) acceptant un `Path`, des `bytes` ou un flux binaire en mémoire, indexation des profils adultes (`build_adult_profiles_index`), extraction/dédoublonnage/tri des parents (`extract_and_group_parents`) et lecture du classeur `ContactsParents.xlsx` (`read_parent_contacts_excel`).
3. `sgdf_contacts/exporters/` : export Excel (`write_parent_contacts_workbook`) supportant l'écriture sur disque (`Path`) et en mémoire (`io.BytesIO`), et export vCard 3.0 (`format_parent_vcard`, `write_vcf_file`, `format_vcf_content`) supportant la génération directe depuis `list[ParentContact]` en mémoire aussi bien que depuis `list[ParentContactCard]`.

Les scripts `extract_parent_contacts.py` et `generate_contacts_vcf.py` à la racine du dépôt sont conservés comme points d'entrée CLI rétrocompatibles qui délèguent au package `sgdf_contacts` et ré-exportent les symboles publics attendus par les tests existants.

## Technical Context

**Language/Version**: Python 3.14 (fourni par l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv`)

**Primary Dependencies**: `beautifulsoup4`, `lxml`, `openpyxl`, bibliothèque standard Python (`argparse`, `collections.abc`, `dataclasses`, `io`, `pathlib`, `re`, `sys`, `typing`, `unicodedata`, `zipfile`), `pytest` et `ruff`

**Storage**: Fichiers locaux (`ExportIndividus.xls` en lecture seule → `ContactsParents.xlsx` → `ContactParents.vcf`, tous exclus du suivi Git via `.gitignore`) et flux binaires en mémoire (`bytes`, `io.BytesIO`)

**Testing**: `pytest` (tests existants dans `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py` + nouveaux tests unitaires dédiés au package `tests/test_sgdf_contacts_package.py`) et `ruff check .`

**Target Platform**: Environnement éphémère Linux / macOS activé par `direnv`

**Project Type**: Package Python modulaire (`sgdf_contacts/`) + scripts CLI d'automatisation Python 3 à la racine

**Performance Goals**: Exécution complète de l'extraction et de la génération `.vcf` (sur disque ou en mémoire) en moins de 5 secondes pour un groupe scout standard (< 500 lignes)

**Constraints**: Identifiants de code en anglais et commentaires, docstrings, messages utilisateur et documentation (`README.md`) en français (Principe I, constitution v2.1.0) ; environnement éphémère Nix/Devbox sans dépendance supplémentaire (Principe II) ; rétrocompatibilité CLI complète (Principe III) ; lecture seule stricte des fichiers d'entrée et zéro donnée personnelle dans le code ou les tests (Principe IV) ; simplicité et absence de dépendance externe dans `sgdf_contacts/domain/` (Principe V — YAGNI) ; travail sur branche dédiée `007-extraire-package-sgdf-contacts` (Principe VI)

**Scale/Scope**: 153 lignes dans `ExportIndividus.xls` → 134 parents uniques sur 13 colonnes dans l'onglet `ContactsParents` de `ContactsParents.xlsx` → 134 fiches `VCARD` dans `ContactParents.vcf`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution (v2.1.0) | Statut | Justification de conformité |
| -------------------------------------- | -------- | ----------------------------- |
| **I. Code en Anglais et Documentation en Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Tous les noms de modules (`sgdf_contacts`, `domain`, `parsers`, `exporters`), classes, fonctions, propriétés (`waha_chat_id`, `to_vcard_card`), variables et paramètres sont en anglais (PEP 8). Tous les commentaires, docstrings, messages CLI et le fichier `README.md` sont en français. |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | Aucune nouvelle bibliothèque externe n'est introduite ; tout fonctionne dans l'environnement éphémère existant (`flake.nix` / `devbox.json` + `direnv`). |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Le découpage en package `sgdf_contacts/` renforce la modularité tout en préservant à l'identique les scripts CLI `extract_parent_contacts.py` et `generate_contacts_vcf.py` (arguments `--input`/`--output`, messages en français, codes de retour `0`/`1`). |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | Lecture seule stricte de `ExportIndividus.xls` et `ContactsParents.xlsx`. Aucune donnée personnelle réelle dans le code ou les tests. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | Séparation claire en 3 sous-packages (`domain`, `parsers`, `exporters`) utilisant uniquement la bibliothèque standard Python dans `domain` et les bibliothèques déjà présentes (`beautifulsoup4`, `lxml`, `openpyxl`) dans `parsers` et `exporters`. |
| **VI. Flux Git par Branche Dédiée et Pull Request (Squash and Merge)** | ✅ CONFORME | Travail réalisé intégralement sur la branche dédiée `007-extraire-package-sgdf-contacts` créée depuis `main`. |

## Project Structure

### Documentation (this feature)

```text
specs/007-extraire-package-sgdf-contacts/
├── plan.md                                  # Ce fichier (/speckit.plan)
├── research.md                              # Décisions techniques Phase 0
├── data-model.md                            # Modèle de données du package sgdf_contacts Phase 1
├── quickstart.md                            # Guide de validation de bout en bout Phase 1
├── contracts/                               # Contrats d'interface Phase 1
│   └── contrat-package-et-cli.md            # Contrat de l'API publique sgdf_contacts et rétrocompatibilité CLI
└── tasks.md                                 # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
sgdf_contacts/
├── __init__.py                              # Ré-exports publics principaux du package
├── domain/
│   ├── __init__.py                          # Export des entités, constantes, exceptions et fonctions de normalisation
│   ├── constants.py                         # Constantes partagées (PARENT_CONTACTS_HEADERS, ADULT_ROLE_LABELS, DEFAULT_CATEGORIES, noms de feuilles/fichiers)
│   ├── exceptions.py                        # Exceptions métier (ContactExtractionError, VcfGenerationError)
│   ├── models.py                            # Entités métier (AttachedChild, AdultGroupProfile, ParentContact avec waha_chat_id et to_vcard_card, ParentContactCard)
│   └── normalization.py                     # Fonctions pures (clean_whitespace, clean_text, normalize_last_name, normalize_first_name, normalize_phone, is_valid_mobile_phone, strip_accents, parent_sort_key, normalize_short_unit, normalize_adult_role, extract_delegation_roles, normalize_address_part, join_street_lines)
├── parsers/
│   ├── __init__.py                          # Export des parseurs d'entrée
│   ├── individuals_xls.py                   # Lecture HTML/XLS (Path | bytes | BinaryIO) et extraction/regroupement (read_individuals_export_table, build_adult_profiles_index, extract_and_group_parents)
│   └── parents_excel.py                     # Lecture de l'onglet ContactsParents depuis un classeur Excel (read_parent_contacts_excel)
└── exporters/
    ├── __init__.py                          # Export des générateurs Excel et vCard
    ├── excel.py                             # Écriture Excel sur disque (Path) ou en mémoire (BytesIO) (auto_fit_column_widths, write_parent_contacts_workbook)
    └── vcard.py                             # Génération vCard 3.0 depuis ParentContact ou ParentContactCard (escape_vcard_value, format_children_with_units, build_parent_note, to_contact_card, format_parent_vcard, format_vcf_content, write_vcf_file)
extract_parent_contacts.py                   # Point d'entrée CLI d'extraction délégant à sgdf_contacts
generate_contacts_vcf.py                     # Point d'entrée CLI vCard délégant à sgdf_contacts
README.md                                    # Documentation mise à jour avec la présentation du package sgdf_contacts
tests/
├── test_environment.py                      # Inchangé : tests de l'environnement éphémère
├── test_extract_parent_contacts.py          # Conservé : vérifie la rétrocompatibilité complète de extract_parent_contacts.py
├── test_generate_contacts_vcf.py            # Conservé : vérifie la rétrocompatibilité complète de generate_contacts_vcf.py
└── test_sgdf_contacts_package.py            # Nouveau : tests unitaires et d'intégration du package sgdf_contacts (absence de duplication, lecture bytes, export BytesIO, export vCard direct depuis list[ParentContact], waha_chat_id)
```

**Structure Decision**: Création du package `sgdf_contacts/` structuré en trois sous-packages (`domain`, `parsers`, `exporters`) à la racine du dépôt, maintien des deux scripts CLI `extract_parent_contacts.py` et `generate_contacts_vcf.py` à la racine comme façades CLI rétrocompatibles, et ajout de `tests/test_sgdf_contacts_package.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution.
