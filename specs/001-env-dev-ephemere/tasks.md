---

description: "Liste des tâches pour l'implémentation de l'environnement de développement éphémère double option"
---

# Tasks: Environnement de Développement Éphémère Double Option (Nix Flake et Devbox)

**Input**: Documents de conception depuis `/specs/001-env-dev-ephemere/`

**Prerequisites**: `plan.md` (requis), `spec.md` (requis pour les récits utilisateurs), `research.md`, `data-model.md`, `contracts/contrat-environnement.md`, `quickstart.md`

**Tests**: Inclus conformément au plan d'implémentation (`tests/test_environnement.py`) pour vérifier automatiquement la parité entre `flake.nix` et `devbox.json`, la matrice `.envrc` et la lecture seule de `ExportIndividus.xls`.

**Organization**: Les tâches sont regroupées par récit utilisateur (User Story) afin de permettre une implémentation et une validation indépendantes de chaque incrément.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Exécutable en parallèle (fichiers distincts, aucune dépendance sur une tâche inachevée)
- **[Story]**: Récit utilisateur auquel appartient la tâche (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- Chaque description inclut le chemin exact du fichier concerné

## Path Conventions

- **Racine du dépôt** : `.envrc`, `flake.nix`, `flake.lock`, `devbox.json`, `.gitignore`, `LISEZMOI.md`
- **Tests automatisés** : `tests/test_environnement.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialisation de l'arborescence et protection des données personnelles et des caches techniques

- [X] T001 Créer le répertoire de tests automatisés du projet dans `tests/`
- [X] T002 [P] Créer le fichier d'exclusion Git excluant les caches d'environnement éphémère (`.direnv/`, `.devbox/`, `.envrc.local`), les caches Python (`__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`) et les fichiers de données personnelles SGDF (`*.xls`, `*.xlsx`, `*.csv`, `ExportIndividus*`) dans `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Socle de vérification de l'environnement Python 3 et de ses bibliothèques requis pour valider toutes les User Stories

**⚠️ CRITICAL**: Ce socle prépare la validation automatisée de chaque option d'environnement

- [X] T003 Créer le module de test initial en français vérifiant la présence de Python 3, l'importation des bibliothèques requises (`pandas`, `bs4`, `lxml`, `xlrd`, `openpyxl`, `pytest`), la disponibilité de `ruff` et la lecture seule non destructive de `ExportIndividus.xls` dans `tests/test_environnement.py`

**Checkpoint**: Socle de test prêt — l'implémentation des définitions d'environnement et de l'activation automatique peut démarrer.

---

## Phase 3: User Story 1 - Activation automatique de l'environnement à l'ouverture du dossier (Priority: P1) 🎯 MVP

**Goal**: Activer automatiquement l'environnement éphémère Python 3 dès l'entrée dans le répertoire grâce à `direnv` et `.envrc`, et restaurer l'état initial du système hôte à la sortie du dossier.

**Independent Test**: Autoriser `.envrc` avec `direnv allow`, vérifier que l'environnement Python 3 isolé est chargé automatiquement avec un message d'accueil en français, et vérifier son déchargement à la sortie du dossier.

### Implementation for User Story 1

- [X] T004 [US1] Créer le script d'activation automatique initial pour `direnv` chargeant optionnellement `.envrc.local` (`source_env_if_exists .envrc.local`), surveillant `flake.nix` et `devbox.json`, et affichant les messages d'état en français dans `.envrc`
- [X] T005 [US1] Ajouter les tests vérifiant l'existence de `.envrc`, la présence de textes exclusivement en français et l'isolation de l'interpréteur `python3` (provenant du store Nix ou de Devbox) dans `tests/test_environnement.py`

**Checkpoint**: Le mécanisme d'activation automatique par `.envrc` est en place et testable.

---

## Phase 4: User Story 2 - Utilisation de l'option Nix Flake (`flake.nix`) (Priority: P1)

**Goal**: Fournir une définition reproductible `flake.nix` (et son `flake.lock`) exposant directement Python 3, les bibliothèques `pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest` ainsi que `ruff` avec un accueil en français.

**Independent Test**: Exécuter `nix develop --command pytest` pour vérifier que Python 3, toutes les bibliothèques SGDF et `ruff` sont immédiatement opérationnels sans `pip` ni `.venv`.

### Implementation for User Story 2

- [X] T006 [P] [US2] Créer la définition déclarative Nix Flakes avec `description` en français, `outputs.devShells.<system>.default` fournissant `pkgs.python3.withPackages (ps: with ps; [ pandas beautifulsoup4 lxml xlrd openpyxl pytest ])` et `pkgs.ruff`, ainsi qu'un `shellHook` en français dans `flake.nix`
- [X] T007 [US2] Générer et valider le fichier de verrouillage reproductible Nix Flakes dans `flake.lock`
- [X] T008 [US2] Ajouter les tests vérifiant le contenu déclaratif de `flake.nix` (présence de Python 3, des paquets `pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff` et des messages en français) ainsi que l'existence de `flake.lock` dans `tests/test_environnement.py`

**Checkpoint**: L'option Nix Flake (`flake.nix`) est complète, verrouillée et validée de bout en bout.

---

## Phase 5: User Story 3 - Utilisation de l'option Jetify Devbox (`devbox.json`) (Priority: P1)

**Goal**: Fournir une définition `devbox.json` fonctionnellement identique à `flake.nix`, exposant la même pile Python 3 et les mêmes paquets Nix avec des scripts et messages d'initialisation en français.

**Independent Test**: Valider la syntaxe JSON et vérifier que la liste des paquets de `devbox.json` est en parité stricte à 100 % avec celle de `flake.nix`.

### Implementation for User Story 3

- [X] T009 [P] [US3] Créer la définition Jetify Devbox déclarant `python3`, `python3Packages.pandas`, `python3Packages.beautifulsoup4`, `python3Packages.lxml`, `python3Packages.xlrd`, `python3Packages.openpyxl`, `python3Packages.pytest`, `ruff`, un `shell.init_hook` en français et les `shell.scripts` (`verifier_environnement`, `tester`, `verifier_qualite`) dans `devbox.json`
- [X] T010 [US3] Ajouter les tests vérifiant la validité JSON de `devbox.json`, la présence des scripts en français et la parité stricte à 100 % des paquets entre `devbox.json` et `flake.nix` dans `tests/test_environnement.py`

**Checkpoint**: Les deux options parallèles (`flake.nix` et `devbox.json`) offrent des capacités strictement équivalentes.

---

## Phase 6: User Story 4 - Coexistence harmonieuse et bascule simple dans `.envrc` (Priority: P2)

**Goal**: Permettre à `.envrc` de gérer la coexistence sans conflit entre `flake.nix` et `devbox.json` selon la variable `OUTIL_ENVIRONNEMENT` (`auto` | `flake` | `devbox`, défaut : `auto`), avec priorité par défaut à `flake.nix` et repli automatique sur `devbox.json`.

**Independent Test**: Tester les différents modes de `OUTIL_ENVIRONNEMENT` (`auto`, `flake`, `devbox` et valeur invalide) et vérifier que le bon gestionnaire ou le message d'erreur en français approprié est sélectionné sans double chargement.

### Implementation for User Story 4

- [X] T011 [US4] Implémenter dans `.envrc` la matrice de décision complète basée sur `OUTIL_ENVIRONNEMENT` (`auto`, `flake`, `devbox` ; défaut : `auto`) avec priorité à `flake.nix` si `nix` est présent, repli automatique sur `devbox.json` si seul `devbox` est présent, et messages d'erreur explicites en français dans `.envrc`
- [X] T012 [US4] Ajouter les tests de la logique de sélection `OUTIL_ENVIRONNEMENT` (`auto`, `flake`, `devbox` et valeurs invalides) et des messages en français de `.envrc` dans `tests/test_environnement.py`

**Checkpoint**: Toutes les User Stories (US1 à US4) sont fonctionnelles et vérifiables indépendamment.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation en français pour les bénévoles et validation finale de qualité

- [X] T013 [P] Rédiger la documentation utilisateur en français expliquant les prérequis, l'activation automatique via `direnv allow`, l'utilisation de `flake.nix` et `devbox.json`, et la bascule via `OUTIL_ENVIRONNEMENT` ou `.envrc.local` dans `LISEZMOI.md`
- [X] T014 Exécuter le vérificateur de qualité et de style `ruff check` au sein de l'environnement éphémère sur `tests/test_environnement.py`
- [X] T015 Exécuter la suite complète de tests `pytest` dans l'environnement éphémère pour valider tous les scénarios de `specs/001-env-dev-ephemere/quickstart.md` via `tests/test_environnement.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** : Aucune dépendance — peut démarrer immédiatement.
- **Foundational (Phase 2)** : Dépend de la Phase 1 (`T001`) — prépare le harnais de test dans `tests/test_environnement.py`.
- **User Stories (Phases 3 à 6)** : Dépendent de la Phase 2 :
  - `T006` (`flake.nix` - US2) et `T009` (`devbox.json` - US3) portent sur des fichiers distincts et peuvent être réalisés en parallèle `[P]`.
  - La Phase 6 (US4 - matrice complète `.envrc`) finalise l'orchestration entre `flake.nix` (US2) et `devbox.json` (US3).
- **Polish (Phase 7)** : Dépend de la complétion des Phases 3 à 6.

### User Story Dependencies

- **User Story 1 (P1)** : Démarre après la Phase 2 ; met en place `.envrc` et la validation d'isolation.
- **User Story 2 (P1)** : Démarre après la Phase 2 ; fournit `flake.nix` et `flake.lock` sans dépendre de `devbox.json`.
- **User Story 3 (P1)** : Démarre après la Phase 2 ; fournit `devbox.json` sans dépendre de `flake.nix` (seul le test de parité `T010` compare les deux fichiers).
- **User Story 4 (P2)** : S'appuie sur `.envrc` (US1), `flake.nix` (US2) et `devbox.json` (US3) pour valider la bascule complète `OUTIL_ENVIRONNEMENT`.

### Parallel Opportunities

- `T001` et `T002` peuvent être exécutées en parallèle lors de la Phase 1.
- `T006` (`flake.nix` dans US2) et `T009` (`devbox.json` dans US3) touchent des fichiers distincts et peuvent être réalisées en parallèle.
- `T013` (`LISEZMOI.md` en Phase 7) peut être rédigée en parallèle de la finalisation des tests.

---

## Parallel Example: User Stories 2 & 3

```bash
# Création en parallèle des deux définitions d'environnement déclaratives :
Tâche T006 [P] [US2]: "Créer la définition déclarative Nix Flakes dans flake.nix"
Tâche T009 [P] [US3]: "Créer la définition Jetify Devbox dans devbox.json"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Compléter la Phase 1 : Setup (`tests/`, `.gitignore`)
2. Compléter la Phase 2 : Foundational (`tests/test_environnement.py`)
3. Compléter les Phases 3 et 4 (`.envrc` + `flake.nix` / `flake.lock`)
4. **STOP et VALIDATION** : Vérifier que l'environnement s'active automatiquement et exécute `pytest` et `ruff`.

### Incremental Delivery

1. Setup + Foundational → Socle et protection RGPD (`.gitignore`) prêts
2. Ajout de US1 + US2 (`flake.nix` + `.envrc`) → Environnement Nix Flake opérationnel (MVP)
3. Ajout de US3 (`devbox.json`) → Parité complète avec Jetify Devbox
4. Ajout de US4 (sélecteur `OUTIL_ENVIRONNEMENT` dans `.envrc`) → Coexistence et bascule sans conflit
5. Phase 7 (`LISEZMOI.md` + validation finale `ruff` / `pytest`) → Livraison complète documentée en français
