# Implementation Plan: Génération du Fichier d'Import Google Contacts (`ContactParents.vcf`)

**Branch**: `003-generer-contacts-vcf` | **Date**: 2026-10-16 | **Spec**: [specs/003-generer-contacts-vcf/spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-generer-contacts-vcf/spec.md`

## Summary

Développer un script Python 3 (`generer_contacts_vcf.py`) en ligne de commande qui lit en lecture seule l'onglet `ContactsParents` du classeur Excel `ContactsParents.xlsx` et génère le fichier `ContactParents.vcf` au format vCard 3.0 (UTF-8) directement importable dans Google Contacts. Chaque fiche vCard contient l'identité du parent (`N:NOM;Prénom;;;` et `FN:Prénom NOM`), ses numéros de téléphone renseignés (portable principal, portable secondaire, fixe domicile), son adresse email, son adresse physique, une note structurée (`Enfants : Prénom NOM (Unité), ...`, suivie sur des lignes distinctes de `Numéro d'adhérent : ...` s'il existe et de `Remarques : ...` si elles existent), ainsi que les étiquettes `"SGDF"` et `"La Rochelle"` (`CATEGORIES:SGDF,La Rochelle`).

## Technical Context

**Language/Version**: Python 3.14 (fourni par l'environnement éphémère `flake.nix` / `devbox.json` activé par `direnv`)

**Primary Dependencies**: `openpyxl` (lecture en lecture seule de l'onglet `ContactsParents` de `ContactsParents.xlsx`), bibliothèque standard Python (`argparse`, `dataclasses`, `pathlib`, `re`, `sys`), `pytest` et `ruff`

**Storage**: Fichiers locaux uniquement (`ContactsParents.xlsx` en lecture seule en entrée ; `ContactParents.vcf` en sortie, tous deux exclus du suivi Git via `.gitignore`)

**Testing**: `pytest` (tests unitaires sur classeurs `.xlsx` synthétiques anonymisés et tests d'intégration en lecture seule sur `ContactsParents.xlsx`) et `ruff check`

**Target Platform**: Environnement éphémère Linux / macOS activé automatiquement par `direnv`

**Project Type**: Script CLI d'automatisation Python 3

**Performance Goals**: Exécution complète en moins de 1 seconde pour un groupe scout standard (~134–500 fiches de parents)

**Constraints**: 100 % des écrits (noms de fichiers, de fonctions, de variables, de classes, arguments CLI, commentaires et documentation) en français ; lecture seule stricte de `ContactsParents.xlsx` ; aucune donnée personnelle en dur dans le code ou les tests ; exclusion des fichiers `.vcf` dans `.gitignore`

**Scale/Scope**: 134 fiches de parents dans l'onglet `ContactsParents` de `ContactsParents.xlsx` générant 134 entrées `VCARD` dans `ContactParents.vcf`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution | Statut | Justification de conformité |
| ----------------------------- | -------- | ----------------------------- |
| **I. Usage Intégral du Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Le script (`generer_contacts_vcf.py`), le module de test (`tests/test_generer_contacts_vcf.py`), toutes les classes, fonctions, variables, constantes, arguments CLI (`--entree`, `--sortie`) et messages utilisateur sont intégralement rédigés en français. |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | Utilise uniquement Python 3, `openpyxl`, `pytest` et `ruff` déjà fournis par `flake.nix` et `devbox.json` et chargés automatiquement par `direnv` via `.envrc`. Aucune nouvelle dépendance tierce n'est requise. |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Script CLI autonome avec validation explicite de l'existence de `ContactsParents.xlsx` et de l'onglet `ContactsParents`, messages clairs en français sur `stdout`/`stderr` et codes de sortie standards (`0` / `1`). |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | `ContactsParents.xlsx` est ouvert uniquement en lecture seule (vérifié par empreinte SHA-256). Les fichiers `*.vcf` et `ContactParents.vcf` sont ajoutés à `.gitignore`. Aucune donnée personnelle nominative réelle n'est inscrite dans le code source ou les tests. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | Sérialisation vCard 3.0 directe en Python standard sans bibliothèque tierce superflue, code lisible et modulaire en un seul fichier `generer_contacts_vcf.py`. |

## Project Structure

### Documentation (this feature)

```text
specs/003-generer-contacts-vcf/
├── plan.md                                  # Ce fichier (/speckit.plan)
├── research.md                              # Décisions techniques Phase 0
├── data-model.md                            # Modèle de données et mapping vCard Phase 1
├── quickstart.md                            # Guide d'exécution et de validation Phase 1
├── contracts/                               # Contrats d'interface Phase 1
│   └── contrat-cli-et-vcard.md              # Contrat CLI et structure vCard 3.0
└── tasks.md                                 # Liste des tâches Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
extraire_contacts_parents.py                 # Script existant d'extraction vers ContactsParents.xlsx (002)
generer_contacts_vcf.py                      # Nouveau script de génération de ContactParents.vcf (003)
.gitignore                                   # Mis à jour pour exclure *.vcf et ContactParents.vcf
LISEZMOI.md                                  # Documentation mise à jour avec la génération vCard
tests/
├── test_environnement.py                    # Tests de l'environnement éphémère (001)
├── test_extraire_contacts_parents.py        # Tests de l'extraction Excel (002)
└── test_generer_contacts_vcf.py             # Tests unitaires et d'intégration de la génération vCard (003)
```

**Structure Decision**: Placement du script `generer_contacts_vcf.py` à la racine du dépôt aux côtés de `extraire_contacts_parents.py` pour offrir une utilisation cohérente et immédiate (`python3 generer_contacts_vcf.py`), accompagné de sa suite de tests dédiée dans `tests/test_generer_contacts_vcf.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution.
