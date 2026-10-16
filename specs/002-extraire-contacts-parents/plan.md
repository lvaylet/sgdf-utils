# Implementation Plan: Extraction et Regroupement des Contacts des Parents SGDF

**Branch**: `002-extraire-contacts-parents` | **Date**: 2026-10-16 | **Spec**: [specs/002-extraire-contacts-parents/spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-extraire-contacts-parents/spec.md`

## Summary

Développer un script Python 3 (`extraire_contacts_parents.py`) en ligne de commande qui lit en lecture seule le fichier d'export SGDF `ExportIndividus.xls` (tableau HTML encodé en `.xls`), extrait les représentants légaux (`1`, `2`, `3`) de tous les jeunes scouts (`Inscrit(e)`, `Pré-inscrit(e)`, `Invité(e)`), les dédoublonne sur le couple `(Nom, Prénom)` pour regrouper les fratries et leurs unités courtes (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`), enrichit chaque parent avec son numéro d'adhérent et son rôle adulte éventuel dans le groupe (ex. `Parent Animateur Farfadet`), trie la liste par ordre alphabétique français sur `(Nom, Prénom)` et sauvegarde le résultat dans le classeur Excel `ContactsParents.xlsx` comprenant les onglets `ExportIndividus` et `ContactsParents`.

## Technical Context

**Language/Version**: Python 3.14 (fourni par l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv`)

**Primary Dependencies**: `beautifulsoup4` + `lxml` (lecture fidèle du tableau HTML `ExportIndividus.xls` en préservant le texte des numéros de téléphone), `openpyxl` (génération du classeur `.xlsx` multi-onglets `ContactsParents.xlsx`), `pytest` et `ruff`

**Storage**: Fichiers locaux uniquement (`ExportIndividus.xls` en lecture seule en entrée ; `ContactsParents.xlsx` en sortie, tous deux ignorés par Git via `.gitignore`)

**Testing**: `pytest` (tests unitaires sur données synthétiques anonymisées et tests d'intégration en lecture seule sur `ExportIndividus.xls`) et `ruff check`

**Target Platform**: Environnement éphémère Linux / macOS activé automatiquement par `direnv`

**Project Type**: Script CLI d'automatisation Python 3

**Performance Goals**: Exécution complète en moins de 2 secondes pour un export de groupe SGDF (~150–500 lignes)

**Constraints**: 100 % des écrits (noms de fichiers, de fonctions, de variables, de classes, arguments CLI, commentaires et documentation) en français ; lecture seule stricte de `ExportIndividus.xls` ; aucune donnée personnelle en dur dans le code ou les tests

**Scale/Scope**: 153 lignes dans `ExportIndividus.xls` (95 jeunes, 58 adultes) produisant 134 fiches de parents uniques dans l'onglet `ContactsParents`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution | Statut | Justification de conformité |
|-----------------------------|--------|-----------------------------|
| **I. Usage Intégral du Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Le script (`extraire_contacts_parents.py`), le module de test (`tests/test_extraire_contacts_parents.py`), toutes les classes (`ContactParent`, `EnfantRattache`, `ProfilAdulteGroupe`), fonctions, variables, arguments CLI (`--entree`, `--sortie`) et messages sont intégralement en français. |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | Le script utilise exclusivement les bibliothèques (`beautifulsoup4`, `lxml`, `openpyxl`, `pytest`, `ruff`) déjà déclarées dans `flake.nix` et `devbox.json` et chargées par `.envrc`. |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Script CLI autonome avec gestion explicite des erreurs d'entrée/sortie, messages en français sur `stdout`/`stderr` et codes de retour standards (`0` / `1`). |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | `ExportIndividus.xls` est ouvert uniquement en lecture seule (vérifié par empreinte SHA-256). `ContactsParents.xlsx` (`*.xlsx`) est exclu de Git par `.gitignore`. Les tests unitaires utilisent des données synthétiques fictives et les tests d'intégration vérifient uniquement des invariants structurels et statistiques sans exposer de données nominatives. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | Architecture claire en un seul script Python 3 modulaire et bien structuré (`extraire_contacts_parents.py`), directement exécutable et facile à maintenir par tout bénévole. |

## Project Structure

### Documentation (this feature)

```text
specs/002-extraire-contacts-parents/
├── plan.md                                  # Ce fichier (/speckit.plan)
├── research.md                              # Décisions techniques Phase 0
├── data-model.md                            # Modèle de données et règles de fusion Phase 1
├── quickstart.md                            # Scénarios de validation Phase 1
├── contracts/                               # Contrats d'interface Phase 1
│   └── contrat-cli-et-colonnes.md           # Contrat CLI et spécification des 11 colonnes Excel
└── tasks.md                                 # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
extraire_contacts_parents.py                 # Script principal d'extraction, dédoublonnage, tri et génération Excel
LISEZMOI.md                                  # Documentation mise à jour avec le guide d'utilisation du script
tests/
├── test_environnement.py                    # Tests existants de l'environnement éphémère (001)
└── test_extraire_contacts_parents.py        # Tests unitaires et d'intégration de l'extraction des contacts parents (002)
```

**Structure Decision**: Placement du script `extraire_contacts_parents.py` directement à la racine du dépôt pour permettre une invocation immédiate (`python3 extraire_contacts_parents.py`) dès l'entrée dans le dossier, accompagné de sa suite de tests dédiée dans `tests/test_extraire_contacts_parents.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution.
