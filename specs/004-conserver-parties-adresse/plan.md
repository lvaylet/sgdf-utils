# Implementation Plan: Conservation des Parties Brutes de l'Adresse de Bout en Bout

**Branch**: `004-conserver-parties-adresse` | **Date**: 2026-10-16 | **Spec**: [specs/004-conserver-parties-adresse/spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-conserver-parties-adresse/spec.md`

## Summary

Simplifier la gestion des adresses postales de bout en bout entre `extraire_contacts_parents.py` et `generer_contacts_vcf.py` en supprimant l'assemblage d'une chaîne unique `Adresse physique` suivi de son redécoupage par expression régulière. Lors de l'extraction depuis `ExportIndividus.xls`, l'adresse de chaque parent est conservée sous forme de 3 composantes distinctes (`Rue` regroupant `Adresse.Ligne1..3`, `Code postal` issu de `Adresse.CodePostal` et `Ville` issue de `Adresse.Municipalite`, en omettant `Adresse.Pays`) enregistrées dans 3 colonnes dédiées de l'onglet `ContactsParents` (portant le schéma à 13 colonnes). Lors de la génération de `ContactParents.vcf`, ces 3 colonnes sont lues et injectées directement dans les sous-champs `<rue>`, `<ville>` et `<code_postal>` de la propriété vCard `ADR;TYPE=HOME` sans aucun redécoupage.

## Technical Context

**Language/Version**: Python 3.14 (fourni par l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv`)

**Primary Dependencies**: `beautifulsoup4`, `lxml`, `openpyxl`, bibliothèque standard Python (`argparse`, `dataclasses`, `pathlib`, `re`, `sys`, `unicodedata`), `pytest` et `ruff`

**Storage**: Fichiers locaux (`ExportIndividus.xls` en lecture seule → `ContactsParents.xlsx` → `ContactParents.vcf`, tous exclus du suivi Git via `.gitignore`)

**Testing**: `pytest` (tests unitaires et tests d'intégration de bout en bout sur données synthétiques et sur `ExportIndividus.xls` / `ContactsParents.xlsx` réels) et `ruff check .`

**Target Platform**: Environnement éphémère Linux / macOS activé par `direnv`

**Project Type**: Scripts CLI d'automatisation Python 3

**Performance Goals**: Exécution complète de l'extraction et de la génération `.vcf` en moins de 5 secondes pour un groupe scout standard (< 500 lignes)

**Constraints**: 100 % des écrits en français (Principe I) ; environnement éphémère Nix/Devbox sans dépendance supplémentaire (Principe II) ; lecture seule stricte des fichiers d'entrée et zéro donnée personnelle dans le code ou les tests (Principe IV) ; suppression du code complexe d'assemblage/redécoupage d'adresse (Principe V — YAGNI)

**Scale/Scope**: 153 lignes dans `ExportIndividus.xls` → 134 parents uniques sur 13 colonnes dans l'onglet `ContactsParents` de `ContactsParents.xlsx` → 134 fiches `VCARD` dans `ContactParents.vcf`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution | Statut | Justification de conformité |
| ----------------------------- | -------- | ----------------------------- |
| **I. Usage Intégral du Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Tous les nouveaux identifiants (`assembler_rue`, `rue`, `code_postal`, `ville`), les en-têtes Excel (`Rue`, `Code postal`, `Ville`), les tests et la documentation (`LISEZMOI.md`) sont intégralement en français. |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | Aucune nouvelle dépendance requise ; utilise l'environnement Python 3 existant fourni par `flake.nix` / `devbox.json` et activé par `direnv`. |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Les deux scripts CLI autonomes (`extraire_contacts_parents.py` et `generer_contacts_vcf.py`) conservent leurs interfaces CLI en français et leur validation stricte des en-têtes Excel (13 colonnes). |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | Lecture seule stricte de `ExportIndividus.xls` et `ContactsParents.xlsx` (vérifiée par empreinte SHA-256). Aucune donnée nominative réelle dans le code ou les tests. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | Remplace le cycle complexe d'assemblage (`assembler_adresse_physique`) et de redécoupage par expression régulière (`decomposer_adresse_postale`) par une conservation directe des 3 composantes `Rue`, `Code postal`, `Ville`. |

## Project Structure

### Documentation (this feature)

```text
specs/004-conserver-parties-adresse/
├── plan.md                                  # Ce fichier (/speckit.plan)
├── research.md                              # Décisions techniques Phase 0
├── data-model.md                            # Modèle de données à 13 colonnes et mapping ADR Phase 1
├── quickstart.md                            # Guide de validation de bout en bout Phase 1
├── contracts/                               # Contrats d'interface Phase 1
│   └── contrat-colonnes-et-vcard.md         # Contrat des 13 colonnes Excel et du champ ADR vCard
└── tasks.md                                 # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
extraire_contacts_parents.py                 # Mis à jour : extraction de Rue, Code postal, Ville (13 colonnes)
generer_contacts_vcf.py                      # Mis à jour : lecture directe de Rue, Code postal, Ville vers ADR
LISEZMOI.md                                  # Mis à jour : description des 13 colonnes de ContactsParents
tests/
├── test_environnement.py                    # Tests de l'environnement éphémère (001)
├── test_extraire_contacts_parents.py        # Mis à jour : tests d'extraction sur 13 colonnes et fusion d'adresse
└── test_generer_contacts_vcf.py             # Mis à jour : tests d'affectation directe ADR sans redécoupage
```

**Structure Decision**: Modification en place des deux scripts existants (`extraire_contacts_parents.py` et `generer_contacts_vcf.py`), de leurs suites de tests respectives dans `tests/` et de la documentation `LISEZMOI.md`, conformément à l'architecture simple et modulaire du dépôt.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution (cette fonctionnalité réduit la complexité globale du code).
