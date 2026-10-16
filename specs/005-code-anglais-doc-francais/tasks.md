---

description: "Liste des tâches pour le passage du code en anglais, le maintien des commentaires en français et le renommage en README.md"
---

# Tasks: Code en Anglais, Commentaires en Français et Renommage en `README.md`

**Input**: Documents de conception depuis `/specs/005-code-anglais-doc-francais/`

**Prerequisites**: `plan.md` (requis), `spec.md` (requis pour les récits utilisateurs), `research.md`, `data-model.md`, `contracts/contrat-identifiants-et-cli.md`, `quickstart.md`

**Tests**: Inclus conformément à `spec.md` (`FR-007`) et `plan.md` (`tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) pour valider unitairement et de bout en bout les 3 User Stories.

**Organization**: Les tâches sont organisées par récit utilisateur (User Story) afin que chaque incrément puisse être implémenté et testé indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Exécutable en parallèle (fichiers distincts, aucune dépendance sur une tâche inachevée)
- **[Story]**: Récit utilisateur auquel appartient la tâche (`[US1]`, `[US2]`, `[US3]`)
- Chaque description inclut le chemin exact du ou des fichiers concernés

## Path Conventions

- **Environnement déclaratif** : `.envrc`, `flake.nix`, `devbox.json`
- **Documentation** : `README.md` (remplace `LISEZMOI.md`)
- **Script d'extraction Excel** : `extract_parent_contacts.py` (remplace `extraire_contacts_parents.py`)
- **Script de génération vCard** : `generate_contacts_vcf.py` (remplace `generer_contacts_vcf.py`)
- **Tests automatisés** : `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Mise en conformité en anglais des identifiants des fichiers de configuration de l'environnement éphémère (`.envrc`, `flake.nix`, `devbox.json`) tout en conservant les commentaires et les messages d'accueil en français

- [X] T001 [P] Mettre à jour les identifiants shell en anglais (`ENV_TOOL`, `selected_tool`, `activate_flake`, `activate_devbox`) tout en conservant les commentaires et messages `echo` en français dans `.envrc`
- [X] T002 [P] Mettre à jour les identifiants Nix en anglais (`supportedSystems`, `forEachSystem`, `system`, `pythonEnv`, `pythonPackages`) tout en conservant la description, les commentaires et le `shellHook` en français dans `flake.nix`
- [X] T003 [P] Mettre à jour les noms de scripts en anglais (`check_environment`, `test`, `check_quality`) tout en conservant les messages `init_hook` en français dans `devbox.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Validation automatisée du socle d'environnement avec des identifiants de test 100 % en anglais et suppression de l'ancien fichier de test en français

**⚠️ CRITICAL**: Ce socle valide l'environnement éphémère avant l'exécution des User Stories

- [X] T004 Créer `tests/test_environment.py` (et supprimer `tests/test_environnement.py`) avec l'ensemble des constantes, fonctions de test et variables en anglais (`PROJECT_ROOT`, `REQUIRED_PYTHON_MODULES`, `EXPECTED_NIX_PACKAGES`, `compute_sha256_digest`, `test_python_version_and_isolation`, `test_sgdf_libraries_import`, `test_cli_tools_availability`, `test_flake_nix_compliance_and_lockfile`, `test_devbox_json_compliance_and_parity`, `test_envrc_decision_matrix`, `test_gitignore_data_protection`, `test_individuals_export_read_only`) et tous les commentaires/docstrings en français dans `tests/test_environment.py`

**Checkpoint**: Le socle d'environnement éphémère et sa suite de tests (`pytest tests/test_environment.py`) sont opérationnels avec un code 100 % en anglais et des commentaires en français.

---

## Phase 3: User Story 1 - Renommage de `LISEZMOI.md` en `README.md` avec contenu en français (Priority: P1) 🎯 MVP

**Goal**: Renommer `LISEZMOI.md` en `README.md` à la racine du dépôt, supprimer `LISEZMOI.md` et mettre à jour les commandes documentées (`extract_parent_contacts.py`, `generate_contacts_vcf.py`, `--input`, `--output`, `ENV_TOOL`) tout en conservant l'intégralité du texte explicatif en français.

**Independent Test**: Vérifier que `README.md` est présent à la racine, que `LISEZMOI.md` n'existe plus, que son contenu est intégralement en français et que toutes les références aux scripts, options CLI et variables d'environnement correspondent au contrat de `contracts/contrat-identifiants-et-cli.md`.

### Implementation for User Story 1

- [X] T005 [US1] Renommer `LISEZMOI.md` en `README.md` (et supprimer `LISEZMOI.md`) en mettant à jour les références à `ENV_TOOL`, `extract_parent_contacts.py`, `generate_contacts_vcf.py` et aux options `--input` / `--output` tout en conservant l'intégralité des explications en français dans `README.md`

**Checkpoint**: `README.md` est en place à la racine du dépôt, rédigé en français et aligné sur les nouveaux noms de scripts et d'options.

---

## Phase 4: User Story 2 - Passage en anglais de l'ensemble du code et de ses identifiants tout en conservant les commentaires en français (Priority: P1)

**Goal**: Remplacer `extraire_contacts_parents.py`, `generer_contacts_vcf.py` et leurs fichiers de tests par `extract_parent_contacts.py`, `generate_contacts_vcf.py`, `tests/test_extract_parent_contacts.py` et `tests/test_generate_contacts_vcf.py` avec 100 % des identifiants en anglais (classes, méthodes, fonctions, constantes, paramètres, variables, options CLI `--input`/`--output`) et 100 % des commentaires, docstrings et messages utilisateur en français.

**Independent Test**: Vérifier l'absence des anciens fichiers `.py` en français, l'absence de tout identifiant en français dans les nouveaux fichiers `.py`, la présence des commentaires/docstrings et messages `--help` en français, et le passage des tests unitaires.

### Tests for User Story 2

- [X] T006 [P] [US2] Créer `tests/test_extract_parent_contacts.py` (et supprimer `tests/test_extraire_contacts_parents.py`) avec tous les identifiants de tests, fixtures, fonctions auxiliaires et variables en anglais et tous les commentaires/docstrings en français dans `tests/test_extract_parent_contacts.py`
- [X] T007 [P] [US2] Créer `tests/test_generate_contacts_vcf.py` (et supprimer `tests/test_generer_contacts_vcf.py`) avec tous les identifiants de tests, fixtures, fonctions auxiliaires et variables en anglais et tous les commentaires/docstrings en français dans `tests/test_generate_contacts_vcf.py`

### Implementation for User Story 2

- [X] T008 [P] [US2] Créer `extract_parent_contacts.py` (et supprimer `extraire_contacts_parents.py`) en implémentant en anglais les entités de `data-model.md` (`AttachedChild` : `"Prénom de l'enfant en casse titre"` pour `first_name`, `"Nom de famille de l'enfant en MAJUSCULES"` pour `last_name`, `"Unité courte (Farfadets, Louveteaux-Jeannettes, etc.)"` pour `short_unit`, `"Statut d'inscription (Inscrit(e), Pré-inscrit(e), Invité(e))"` pour `registration_status`, `"Retourne \"Prénom NOM\""` pour `format_full_name()` ; `AdultGroupProfile` : `last_name`, `first_name`, `member_id`, `roles_and_delegations`, `mobile_phone_1`, `mobile_phone_2`, `home_phone`, `email`, `"Rue normalisée en casse titre (Ligne 1..3)"` pour `street`, `"Code postal"` pour `postal_code`, `"Ville normalisée en casse titre"` pour `city` ; `ParentContact` : `last_name` à `notes_list`, propriétés `children_names`, `children_units`, `notes`, méthodes `add_child`, `add_note`, `merge_contact_info`, `reorganize_phones`, `"Retourne les 13 valeurs de colonnes dans l'ordre"` pour `to_excel_row()`), toutes les fonctions du contrat `contracts/contrat-identifiants-et-cli.md` et les options CLI `-i`/`--input` et `-o`/`--output`, avec tous les commentaires, docstrings et messages utilisateur en français dans `extract_parent_contacts.py`
- [X] T009 [P] [US2] Créer `generate_contacts_vcf.py` (et supprimer `generer_contacts_vcf.py`) en implémentant en anglais l'entité `ParentContactCard` de `data-model.md` (`"Nom de famille (N:<last_name>;...)"` pour `last_name`, `"Prénom (N:...;<first_name>;...)"` pour `first_name`, `primary_mobile_phone`, `secondary_mobile_phone`, `landline_phone`, `email_address`, `children_names`, `children_units`, `"Sous-champ <rue> de ADR;TYPE=HOME"` pour `street`, `"Sous-champ <code_postal> de ADR;TYPE=HOME"` pour `postal_code`, `"Sous-champ <ville> de ADR;TYPE=HOME"` pour `city`, `"Rubrique Numéro d'adhérent : de NOTE"` pour `member_id`, `"Rubrique Remarques : de NOTE"` pour `notes`, `"CATEGORIES:SGDF,La Rochelle"` pour `categories`, `"FN:<Prénom NOM>"` pour `formatted_full_name`), toutes les fonctions du contrat `contracts/contrat-identifiants-et-cli.md` et les options CLI `-i`/`--input` et `-o`/`--output`, avec tous les commentaires, docstrings et messages utilisateur en français dans `generate_contacts_vcf.py`

**Checkpoint**: Tous les fichiers Python et leurs suites de tests sont en anglais avec commentaires et messages en français (`pytest tests/test_extract_parent_contacts.py tests/test_generate_contacts_vcf.py`).

---

## Phase 5: User Story 3 - Continuité fonctionnelle de bout en bout sans régression métier (Priority: P1)

**Goal**: Valider l'exécution complète de bout en bout (`extract_parent_contacts.py` puis `generate_contacts_vcf.py`) sur l'export de référence `ExportIndividus.xls` et vérifier que `ContactsParents.xlsx` (13 colonnes en français, 134 parents) et `ContactParents.vcf` (134 fiches vCard) sont générés sans aucune régression ni modification du fichier d'entrée.

**Independent Test**: Exécuter les deux scripts en séquence avec `--input` et `--output` sur `ExportIndividus.xls` et vérifier l'intégrité SHA-256 de `ExportIndividus.xls` ainsi que les 134 fiches dans `ContactsParents.xlsx` et `ContactParents.vcf`.

### Implementation for User Story 3

- [X] T010 [US3] Exécuter de bout en bout `extract_parent_contacts.py` et `generate_contacts_vcf.py` pour régénérer et vérifier `ContactsParents.xlsx` (13 colonnes, 134 parents) et `ContactParents.vcf` (134 fiches vCard) à partir de `ExportIndividus.xls`

**Checkpoint**: Le flux complet de bout en bout (US1 + US2 + US3) fonctionne sans aucune régression métier.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Contrôle qualité final (`ruff`, `pytest`) et validation complète du guide `quickstart.md`

- [X] T011 Exécuter `ruff check .` et `pytest -v` ainsi que l'ensemble des vérifications de `specs/005-code-anglais-doc-francais/quickstart.md` pour confirmer 0 erreur de style et 100 % de réussite des tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** : Aucune dépendance — `T001`, `T002` et `T003` portent sur des fichiers distincts (`.envrc`, `flake.nix`, `devbox.json`) et peuvent s'exécuter en parallèle.
- **Foundational (Phase 2)** : Dépend de la Phase 1 — `T004` (`tests/test_environment.py`) valide les fichiers mis à jour en Phase 1.
- **User Story 1 (Phase 3 - P1)** : Peut démarrer dès la Phase 1/2 terminée — `T005` renomme et met à jour `README.md`.
- **User Story 2 (Phase 4 - P1)** : Peut démarrer dès la Phase 2 terminée — `T006`, `T007`, `T008` et `T009` portent sur des fichiers distincts et peuvent être menés en parallèle.
- **User Story 3 (Phase 5 - P1)** : Dépend de la Phase 4 (US2) — `T010` exécute le flux complet de bout en bout avec les nouveaux scripts.
- **Polish (Phase 6)** : Dépend des Phases 1 à 5 — `T011` valide `ruff check .`, `pytest -v` et `quickstart.md`.

### Parallel Opportunities

- `T001` (`.envrc`), `T002` (`flake.nix`) et `T003` (`devbox.json`) sont parallélisables.
- `T005` (`README.md`), `T008` (`extract_parent_contacts.py`) et `T009` (`generate_contacts_vcf.py`) portent sur des fichiers distincts.
- `T006` (`tests/test_extract_parent_contacts.py`) et `T007` (`tests/test_generate_contacts_vcf.py`) portent sur des fichiers de test distincts.

---

## Parallel Example: User Story 2

```bash
# Réécriture en parallèle des deux scripts principaux en anglais :
Task: "T008 [P] [US2] Créer extract_parent_contacts.py (et supprimer extraire_contacts_parents.py)"
Task: "T009 [P] [US2] Créer generate_contacts_vcf.py (et supprimer generer_contacts_vcf.py)"

# Réécriture en parallèle des deux suites de tests correspondantes :
Task: "T006 [P] [US2] Créer tests/test_extract_parent_contacts.py (et supprimer tests/test_extraire_contacts_parents.py)"
Task: "T007 [P] [US2] Créer tests/test_generate_contacts_vcf.py (et supprimer tests/test_generer_contacts_vcf.py)"
```

---

## Implementation Strategy

### MVP First (User Story 1 + Socle)

1. Compléter Phase 1 (`T001` à `T003`) et Phase 2 (`T004`)
2. Compléter Phase 3 (`T005` — US1 : `README.md` en français à la racine du dépôt)
3. **STOP et VALIDATION** : Vérifier `test -f README.md && test ! -f LISEZMOI.md` et `pytest tests/test_environment.py`

### Incremental Delivery

1. Ajouter Phase 4 (`T006` à `T009` — US2 : scripts et tests Python 100 % en anglais avec commentaires et messages en français)
2. Ajouter Phase 5 (`T010` — US3 : vérification de bout en bout sans régression sur `ExportIndividus.xls` → `ContactsParents.xlsx` → `ContactParents.vcf`)
3. Compléter Phase 6 (`T011` — validation finale `ruff check .` et `pytest -v`)
