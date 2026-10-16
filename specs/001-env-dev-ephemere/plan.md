# Implementation Plan: Environnement de Développement Éphémère Double Option (Nix Flake et Devbox)

**Branch**: `001-env-dev-ephemere` | **Date**: 2026-10-16 | **Spec**: [specs/001-env-dev-ephemere/spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-env-dev-ephemere/spec.md`

## Summary

Mettre en place un environnement de développement éphémère, reproductible et isolé pour les scripts d'automatisation Python 3 du groupe scout SGDF de La Rochelle, avec deux définitions maintenues en parallèle à la racine du dépôt : `flake.nix` (Nix Flakes) et `devbox.json` (Jetify Devbox). Toutes deux sont activées automatiquement par `direnv` via `.envrc` (avec priorité par défaut à `flake.nix`, repli automatique sur `devbox.json` si Nix est absent, et bascule explicite via `OUTIL_ENVIRONNEMENT`). Les deux options fournissent directement Python 3 et les paquets requis (`pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff`) sans étape `pip` ni `.venv`, accompagnés d'une documentation et de tests de validation intégralement rédigés en français.

## Technical Context

**Language/Version**: Python 3 (fourni via Nixpkgs `python3`, version stable 3.12+) et Bash (pour `.envrc`)

**Primary Dependencies**: Nix (`flakes` + `nix-command`), Jetify Devbox (`devbox`), `direnv`, et paquets Python gérés par Nix/Devbox : `pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff`

**Storage**: Fichiers locaux uniquement (lecture seule des exports SGDF tels que `ExportIndividus.xls` au format HTML/XLS ; aucune base de données)

**Testing**: `pytest` et `ruff` (exécutés directement dans l'environnement éphémère)

**Target Platform**: Linux (dont NixOS) et macOS disposant de `direnv` ainsi que de Nix et/ou Devbox

**Project Type**: Infrastructure d'environnement de développement déclaratif et outillage CLI Python 3

**Performance Goals**: Activation immédiate de l'environnement (< 2 secondes une fois le cache Nix/direnv initialisé) et 0 étape d'installation manuelle (`pip` / `.venv`)

**Constraints**: 100 % des écrits (documentation, commentaires, messages d'accueil/erreur, noms de fichiers et d'identifiants Python) en français ; aucune donnée personnelle d'adhérent ou de parent suivie par Git

**Scale/Scope**: Groupe scout local SGDF La Rochelle ; 2 définitions d'environnement parallèles (`flake.nix`, `devbox.json`), 1 orchestrateur `.envrc`, 1 fichier `.gitignore`, documentation en français (`LISEZMOI.md`) et suite de validation automatisée (`tests/test_environnement.py`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Vérification pré-recherche (Phase 0) et post-conception (Phase 1)

| Principe de la Constitution | Statut | Justification de conformité |
|-----------------------------|--------|-----------------------------|
| **I. Usage Intégral du Français (NON-NÉGOCIABLE)** | ✅ CONFORME | Tous les commentaires (`flake.nix`, `.envrc`), les messages d'accueil et d'erreur, la documentation (`LISEZMOI.md`), les noms de scripts Devbox et les fichiers/fonctions/variables de test (`tests/test_environnement.py`) sont rédigés intégralement en français. Seuls les noms de fichiers imposés par les outils (`.envrc`, `flake.nix`, `devbox.json`, `.gitignore`) conservent leur nom technique obligatoire. |
| **II. Environnement de Développement Éphémère et Déclaratif** | ✅ CONFORME | Double définition déclarative `flake.nix` et `devbox.json` fournissant Python 3 et tous les paquets requis sans `pip` ni installation globale, activée automatiquement par `direnv` via `.envrc`. |
| **III. Automatisation Modulaire en Python 3** | ✅ CONFORME | Le script et les tests de vérification de l'environnement sont écrits en Python 3 avec des diagnostics explicites en français et des codes de sortie standards. |
| **IV. Protection des Données Personnelles et Intégrité des Sources** | ✅ CONFORME | `.gitignore` exclut tous les fichiers d'export (`*.xls`, `*.xlsx`, `*.csv`, `ExportIndividus*`) et les caches locaux (`.direnv/`, `.devbox/`). Le test de lecture sur `ExportIndividus.xls` ouvre le fichier strictement en lecture seule sans jamais afficher ni enregistrer de données nominatives. |
| **V. Simplicité et Maintenabilité pour les Bénévoles** | ✅ CONFORME | Logique `.envrc` concise et lisible, aucun gestionnaire intermédiaire superflu (`poetry`, `pipenv`, `.venv`), parité directe des paquets Nix entre `flake.nix` et `devbox.json`. |

## Project Structure

### Documentation (this feature)

```text
specs/001-env-dev-ephemere/
├── plan.md                          # Ce fichier (sortie de la commande /speckit.plan)
├── research.md                      # Sortie de la Phase 0 (/speckit.plan)
├── data-model.md                    # Sortie de la Phase 1 (/speckit.plan)
├── quickstart.md                    # Sortie de la Phase 1 (/speckit.plan)
├── contracts/                       # Sortie de la Phase 1 (/speckit.plan)
│   └── contrat-environnement.md     # Contrat d'interface de .envrc, flake.nix et devbox.json
└── tasks.md                         # Sortie de la Phase 2 (/speckit.tasks - créé à l'étape suivante)
```

### Source Code (repository root)

```text
.envrc                               # Activation automatique direnv (priorité flake.nix, repli devbox.json, variable OUTIL_ENVIRONNEMENT)
flake.nix                            # Définition d'environnement éphémère Nix Flakes (Python 3 + paquets SGDF + ruff)
flake.lock                           # Fichier de verrouillage Nix Flakes généré pour la reproductibilité
devbox.json                          # Définition d'environnement éphémère Jetify Devbox (parité complète avec flake.nix)
.gitignore                           # Exclusion des caches (.direnv/, .devbox/, __pycache__/) et des données personnelles (*.xls, *.xlsx, *.csv)
LISEZMOI.md                          # Documentation en français pour les bénévoles du groupe SGDF de La Rochelle
tests/
└── test_environnement.py            # Vérification automatisée (pytest) de la parité des paquets, de .envrc et de la lecture seule de ExportIndividus.xls
```

**Structure Decision**: Structure de projet unique à la racine du dépôt, adaptée à un dépôt d'automatisation Python 3 où les fichiers de définition d'environnement (`.envrc`, `flake.nix`, `devbox.json`, `.gitignore`) doivent impérativement résider à la racine pour être détectés automatiquement par `direnv`, `nix` et `devbox` dès l'entrée dans le dossier.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Aucune violation de la constitution. Tous les principes sont respectés sans exception.
