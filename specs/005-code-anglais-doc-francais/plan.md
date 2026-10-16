# Implementation Plan: Code en Anglais, Commentaires en Français et Renommage en `README.md`

**Branch**: `005-code-anglais-doc-francais` | **Date**: 2026-10-16 | **Spec**: [specs/005-code-anglais-doc-francais/spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-code-anglais-doc-francais/spec.md`

## Summary

Mettre l'ensemble du dépôt en conformité avec la constitution v2.0.0 du projet :

1. Renommer `LISEZMOI.md` en `README.md` à la racine du dépôt tout en conservant son contenu explicatif intégralement en français et en mettant à jour les noms de scripts, d'options CLI et de variables d'environnement.
2. Renommer les fichiers Python et leurs suites de tests en anglais (`extract_parent_contacts.py`, `generate_contacts_vcf.py`, `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) et supprimer les anciens fichiers `.py` en français.
3. Traduire en anglais 100 % des identifiants du code source, des tests et des fichiers d'environnement (`.envrc`, `flake.nix`, `devbox.json`), y compris les classes, fonctions, méthodes, constantes, paramètres, variables et options CLI (`-i`/`--input`, `-o`/`--output`), tout en conservant l'intégralité des commentaires, docstrings, messages utilisateur et données/colonnes métiers en français.

## Technical Context

**Language/Version**: Python 3.14 (fourni par l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv`)

**Primary Dependencies**: `beautifulsoup4`, `lxml`, `openpyxl`, bibliothèque standard Python (`argparse`, `dataclasses`, `pathlib`, `re`, `sys`, `unicodedata`, `zipfile`), `pytest` et `ruff`

**Storage**: Fichiers locaux (`ExportIndividus.xls` en lecture seule → `ContactsParents.xlsx` → `ContactParents.vcf`, tous exclus du suivi Git via `.gitignore`)

**Testing**: `pytest` (tests unitaires et d'intégration dans `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) et `ruff check .`

**Target Platform**: Environnement éphémère Linux / macOS activé par `direnv`

**Project Type**: Scripts CLI d'automatisation Python 3

**Performance Goals**: Exécution complète de l'extraction et de la génération `.vcf` en moins de 5 secondes pour un groupe scout standard (< 500 lignes)

**Constraints**: 100 % des identifiants de code en anglais et 100 % des commentaires, docstrings, messages utilisateur et documentation (`README.md`) en français (Principe I, constitution v2.0.0) ; environnement éphémère Nix/Devbox sans dépendance supplémentaire (Principe II) ; lecture seule stricte des fichiers d'entrée et zéro donnée personnelle dans le code ou les tests (Principe IV) ; simplicité et zéro régression métier (Principe V)

**Scale/Scope**: 153 lignes dans `ExportIndividus.xls` → 134 parents uniques sur 13 colonnes dans l'onglet `ContactsParents` de `ContactsParents.xlsx` → 134 fiches `VCARD` dans `ContactParents.vcf`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution (v2.0.0) | Statut | Justification de conformité |
| -------------------------------------- | -------- | ----------------------------- |
| **I. Code en Anglais et Documentation en Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Tous les identifiants de code (fichiers `.py`, classes, fonctions, méthodes, constantes, variables, paramètres, options CLI `--input`/`--output`, identifiants `.envrc`/`flake.nix`/`devbox.json`) sont en anglais. Tous les commentaires, docstrings, messages CLI et le fichier `README.md` restent en français. |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | `flake.nix`, `devbox.json` et `.envrc` conservent exactement les mêmes paquets et la même logique d'activation automatique via `direnv`, avec des identifiants internes en anglais (`ENV_TOOL`, `activate_flake`, `activate_devbox`, `supportedSystems`, `forEachSystem`, `pythonEnv`). |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Les deux scripts CLI autonomes (`extract_parent_contacts.py` et `generate_contacts_vcf.py`) conservent leurs messages explicites en français sur `stdout`/`stderr` et leurs codes de retour standards (`0` / `1`). |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | Lecture seule stricte de `ExportIndividus.xls` et `ContactsParents.xlsx` (vérifiée par empreinte SHA-256). Aucune donnée nominative réelle dans le code ou les tests. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | Traduction directe 1 pour 1 des identifiants en anglais selon PEP 8 sans ajout d'abstraction ni modification de l'algorithme métier. |

## Project Structure

### Documentation (this feature)

```text
specs/005-code-anglais-doc-francais/
├── plan.md                                  # Ce fichier (/speckit.plan)
├── research.md                              # Décisions techniques Phase 0
├── data-model.md                            # Correspondance des entités et attributs en anglais Phase 1
├── quickstart.md                            # Guide de validation de bout en bout Phase 1
├── contracts/                               # Contrats d'interface Phase 1
│   └── contrat-identifiants-et-cli.md       # Contrat des scripts, options CLI, identifiants et sorties métiers
└── tasks.md                                 # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
.envrc                                       # Identifiants shell en anglais (ENV_TOOL, activate_flake, activate_devbox), commentaires et echo en français
flake.nix                                    # Identifiants Nix en anglais (supportedSystems, forEachSystem, pythonEnv), commentaires et shellHook en français
devbox.json                                  # Noms de scripts en anglais (check_environment, test, check_quality), init_hook en français
README.md                                    # Renommé depuis LISEZMOI.md, rédigé en français avec commandes mises à jour
extract_parent_contacts.py                   # Renommé depuis extraire_contacts_parents.py, code 100 % en anglais, commentaires/messages en français
generate_contacts_vcf.py                     # Renommé depuis generer_contacts_vcf.py, code 100 % en anglais, commentaires/messages en français
tests/
├── test_environment.py                      # Renommé depuis test_environnement.py, code 100 % en anglais, commentaires en français
├── test_extract_parent_contacts.py          # Renommé depuis test_extraire_contacts_parents.py, code 100 % en anglais, commentaires en français
└── test_generate_contacts_vcf.py            # Renommé depuis test_generer_contacts_vcf.py, code 100 % en anglais, commentaires en français
```

**Structure Decision**: Renommage en place de `LISEZMOI.md` vers `README.md`, des deux scripts Python principaux et des trois fichiers de tests `pytest` vers des noms en anglais à la racine et dans `tests/`, avec suppression des anciens fichiers portant des noms en français.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution.
