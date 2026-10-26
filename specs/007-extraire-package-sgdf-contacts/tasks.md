---

description: "Liste des tâches pour l'extraction du cœur métier dans le package modulaire sgdf_contacts"
---

# Tasks: Extraction du Cœur Métier dans un Package Modulaire `sgdf_contacts`

**Input**: Documents de conception depuis `/specs/007-extraire-package-sgdf-contacts/`

**Prerequisites**: `plan.md` (requis), `spec.md` (requis pour les récits utilisateurs), `research.md`, `data-model.md`, `contracts/contrat-package-et-cli.md`, `quickstart.md`

**Tests**: Inclus conformément à `spec.md` (`SC-004`) et `plan.md` (`tests/test_sgdf_contacts_package.py` + maintien au vert de `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) pour valider unitairement et de bout en bout les 3 User Stories sans exposer de données personnelles.

**Organization**: Les tâches sont organisées par récit utilisateur (User Story) afin que chaque incrément puisse être implémenté et testé indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Exécutable en parallèle (fichiers distincts, aucune dépendance sur une tâche inachevée)
- **[Story]**: Récit utilisateur auquel appartient la tâche (`[US1]`, `[US2]`, `[US3]`)
- Chaque description inclut le chemin exact du fichier concerné

## Path Conventions

- **Package modulaire** : `sgdf_contacts/` (`domain/`, `parsers/`, `exporters/`)
- **Points d'entrée CLI rétrocompatibles** : `extract_parent_contacts.py`, `generate_contacts_vcf.py`
- **Tests automatisés** : `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`, `tests/test_sgdf_contacts_package.py`
- **Documentation** : `README.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Vérification initiale de l'environnement éphémère Python 3 et création de l'arborescence de répertoires du package `sgdf_contacts`

- [X] T001 Vérifier le bon fonctionnement de l'environnement éphémère en exécutant la suite de tests dans `tests/test_environment.py`
- [X] T002 Créer l'arborescence des répertoires du package `sgdf_contacts/domain/`, `sgdf_contacts/parsers/` et `sgdf_contacts/exporters/` conformément à `specs/007-extraire-package-sgdf-contacts/plan.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Mise en place des constantes et exceptions métier partagées dont dépendent toutes les User Stories

**⚠️ CRITICAL**: Ce socle est requis par toutes les User Stories

- [X] T003 [P] Créer le module des constantes partagées (`PARENT_CONTACTS_HEADERS` : `"tuple des 13 intitulés de colonnes en français de l'onglet ContactsParents"`, `ADULT_ROLE_LABELS` : `"dictionnaire (code_fonction, civilite) -> libellé_français"`, `DEFAULT_CATEGORIES` : `("SGDF", "La Rochelle")`, `SOURCE_SHEET_NAME` : `"ExportIndividus"`, `PARENTS_SHEET_NAME` : `"ContactsParents"`, `DEFAULT_EXPORT_INPUT_FILE` : `"ExportIndividus.xls"`, `DEFAULT_PARENTS_WORKBOOK_FILE` : `"ContactsParents.xlsx"`, `DEFAULT_VCF_OUTPUT_FILE` : `"ContactParents.vcf"`) dans `sgdf_contacts/domain/constants.py`
- [X] T004 [P] Créer le module des exceptions métier (`ContactExtractionError` et `VcfGenerationError`) avec leurs docstrings en français dans `sgdf_contacts/domain/exceptions.py`

**Checkpoint**: Les constantes et exceptions partagées du domaine sont prêtes.

---

## Phase 3: User Story 1 - Mutualisation du cœur métier, des règles de normalisation et des constantes partagées (Priority: P1) 🎯 MVP

**Goal**: Regrouper dans `sgdf_contacts/domain/` (sans aucune dépendance externe hors bibliothèque standard Python) toutes les fonctions pures de nettoyage, normalisation et tri ainsi que les entités métier (`AttachedChild`, `AdultGroupProfile`, `ParentContact` avec la propriété `waha_chat_id` et `to_contact_card()`, `ParentContactCard`).

**Independent Test**: Importer directement `sgdf_contacts.domain` et exécuter les tests unitaires du domaine dans `tests/test_sgdf_contacts_package.py` pour vérifier les fonctions de normalisation, le tri alphabétique français, la conversion `to_contact_card()` et la propriété `waha_chat_id` (`"+33687966975"` → `"33687966975@c.us"`, `""` → `""`).

### Tests for User Story 1

- [X] T005 [P] [US1] Créer les tests unitaires du domaine (`sgdf_contacts.domain`) vérifiant les constantes partagées, les fonctions de normalisation, l'absence de dépendance externe, la propriété `waha_chat_id` (`+33687966975` → `33687966975@c.us` et `""` si vide) et `ParentContact.to_contact_card()` dans `tests/test_sgdf_contacts_package.py`

### Implementation for User Story 1

- [X] T006 [P] [US1] Implémenter les fonctions pures de nettoyage, de normalisation et de tri (`clean_whitespace`, `clean_text`, `normalize_last_name`, `normalize_first_name`, `normalize_phone`, `is_valid_mobile_phone`, `strip_accents`, `parent_sort_key`, `normalize_short_unit`, `normalize_adult_role`, `extract_delegation_roles`, `normalize_address_part`, `join_street_lines`) dans `sgdf_contacts/domain/normalization.py`
- [X] T007 [US1] Implémenter les entités du domaine (`AttachedChild` `frozen=True` avec `format_full_name()`, `AdultGroupProfile`, `ParentContactCard` `frozen=True` avec `categories: tuple[str, ...] = DEFAULT_CATEGORIES` et `formatted_full_name`, et `ParentContact` avec `waha_chat_id` : `"Identifiant WhatsApp WAHA dérivé de primary_mobile_phone (+33687966975 → 33687966975@c.us, ou \"\" si vide)"`, `to_excel_row()` et `to_contact_card()`) dans `sgdf_contacts/domain/models.py`
- [X] T008 [US1] Exporter l'ensemble des entités, constantes, exceptions et fonctions de normalisation dans `sgdf_contacts/domain/__init__.py`

**Checkpoint**: Le sous-package `sgdf_contacts.domain` est complet, sans dépendance externe, et ses tests unitaires dans `tests/test_sgdf_contacts_package.py` passent.

---

## Phase 4: User Story 2 - Lecture et génération des contacts en mémoire ou sur disque sans fichier intermédiaire obligatoire (Priority: P1)

**Goal**: Implémenter `sgdf_contacts/parsers/` (lecture HTML/XLS depuis `Path` ou `bytes`/`BinaryIO` en mémoire, extraction/regroupement des parents, lecture de `ContactsParents.xlsx`) et `sgdf_contacts/exporters/` (écriture Excel vers `Path` ou `io.BytesIO`, et génération vCard 3.0 directe depuis `list[ParentContact]` aussi bien que depuis `list[ParentContactCard]`).

**Independent Test**: Exécuter les tests de `tests/test_sgdf_contacts_package.py` vérifiant la lecture d'un export HTML/XLS depuis des `bytes` en mémoire, l'écriture du classeur Excel dans un `io.BytesIO` et la génération directe d'un contenu/fichier `.vcf` depuis `list[ParentContact]` sans passer par un fichier `.xlsx` intermédiaire.

### Tests for User Story 2

- [X] T009 [P] [US2] Ajouter dans `tests/test_sgdf_contacts_package.py` les tests unitaires et d'intégration de lecture en mémoire (`read_individuals_export_table` avec `bytes` et `io.BytesIO`, y compris les cas d'erreur de flux vide ou invalide), d'export Excel en mémoire (`write_parent_contacts_workbook` avec `io.BytesIO`) et de génération vCard 3.0 directe depuis `list[ParentContact]` (`format_parent_vcard`, `format_vcf_content`, `write_vcf_file`) comparée à la génération via Excel

### Implementation for User Story 2

- [X] T010 [P] [US2] Implémenter le parseur `read_individuals_export_table(input_source: Path | bytes | BinaryIO)` (supportant à la fois un `Path` sur disque et un flux `bytes`/`BinaryIO` en mémoire avec levée de `ContactExtractionError` en français), `build_adult_profiles_index` et `extract_and_group_parents` dans `sgdf_contacts/parsers/individuals_xls.py`
- [X] T011 [P] [US2] Implémenter le lecteur de classeur Excel `read_parent_contacts_excel(input_path: Path) -> list[ParentContactCard]` dans `sgdf_contacts/parsers/parents_excel.py`
- [X] T012 [US2] Exporter les fonctions de lecture et d'extraction (`read_individuals_export_table`, `build_adult_profiles_index`, `extract_and_group_parents`, `read_parent_contacts_excel`) dans `sgdf_contacts/parsers/__init__.py`
- [X] T013 [P] [US2] Implémenter le générateur Excel `auto_fit_column_widths` et `write_parent_contacts_workbook` supportant l'écriture vers un `Path` sur disque et vers un flux binaire en mémoire (`io.BytesIO`) dans `sgdf_contacts/exporters/excel.py`
- [X] T014 [P] [US2] Implémenter le générateur vCard 3.0 (`escape_vcard_value`, `format_children_with_units`, `build_parent_note`, `to_contact_card`, `format_parent_vcard`, `format_vcf_content`, `write_vcf_file`) acceptant directement des `ParentContact` ou des `ParentContactCard` dans `sgdf_contacts/exporters/vcard.py`
- [X] T015 [US2] Exporter les fonctions de génération Excel et vCard dans `sgdf_contacts/exporters/__init__.py` et exposer l'API publique de haut niveau dans `sgdf_contacts/__init__.py`

**Checkpoint**: Le package `sgdf_contacts` (`domain`, `parsers`, `exporters`) est intégralement fonctionnel sur disque et en mémoire.

---

## Phase 5: User Story 3 - Rétrocompatibilité totale des commandes en ligne de commande et des résultats produits (Priority: P1)

**Goal**: Refactoriser `extract_parent_contacts.py` et `generate_contacts_vcf.py` à la racine du dépôt pour qu'ils délèguent toute la logique métier, le parsing et l'export au package `sgdf_contacts` sans aucune duplication, tout en conservant à 100 % la rétrocompatibilité CLI (`--input`, `--output`, `--help`, messages en français, codes de retour) et les symboles ré-exportés attendus par les tests existants.

**Independent Test**: Exécuter `pytest -v` (incluant `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py` et `tests/test_sgdf_contacts_package.py`) et vérifier qu'aucune constante ni fonction métier n'est dupliquée entre les deux scripts CLI.

### Tests for User Story 3

- [X] T016 [P] [US3] Ajouter dans `tests/test_sgdf_contacts_package.py` un test d'inspection vérifiant l'absence de duplication de constantes (`PARENT_CONTACTS_HEADERS`, `ADULT_ROLE_LABELS`, `DEFAULT_CATEGORIES`), de classes et de fonctions métier entre `extract_parent_contacts.py` et `generate_contacts_vcf.py` (vérification d'identité des objets importés `is` avec `sgdf_contacts`)

### Implementation for User Story 3

- [X] T017 [P] [US3] Refactoriser `extract_parent_contacts.py` pour déléguer la lecture, l'extraction et l'écriture Excel à `sgdf_contacts` tout en conservant `run_extraction`, `parse_args`, `main` et les ré-exports publics pour la rétrocompatibilité dans `extract_parent_contacts.py`
- [X] T018 [P] [US3] Refactoriser `generate_contacts_vcf.py` pour déléguer la lecture Excel et la génération vCard 3.0 à `sgdf_contacts` tout en conservant `run_vcf_generation`, `parse_args`, `main` et les ré-exports publics pour la rétrocompatibilité dans `generate_contacts_vcf.py`

**Checkpoint**: Les trois User Stories (US1, US2, US3) sont complètes et 100 % des tests existants et nouveaux passent.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mise à jour de la documentation en français et validation finale de bout en bout

- [X] T019 [P] Mettre à jour `README.md` en français pour documenter l'architecture modulaire du package `sgdf_contacts/` (`domain`, `parsers`, `exporters`) en complément de l'utilisation des scripts CLI dans `README.md`
- [X] T020 Exécuter la validation complète de bout en bout (`pytest -v` et `ruff check .`, ainsi que l'exécution sur `ExportIndividus.xls` s'il est présent) conformément à `specs/007-extraire-package-sgdf-contacts/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** : Aucune dépendance — démarre immédiatement (`T001`, `T002`).
- **Foundational (Phase 2)** : Dépend de la Phase 1 — crée `constants.py` (`T003`) et `exceptions.py` (`T004`).
- **User Story 1 (Phase 3 - P1)** : Dépend de la Phase 2 — crée `normalization.py` (`T006`), `models.py` (`T007`), `domain/__init__.py` (`T008`) et les tests du domaine (`T005`).
- **User Story 2 (Phase 4 - P1)** : Dépend de la Phase 3 (`sgdf_contacts.domain`) — crée en parallèle `parsers/` (`T010`, `T011`, `T012`) et `exporters/` (`T013`, `T014`, `T015`) ainsi que leurs tests en mémoire (`T009`).
- **User Story 3 (Phase 5 - P1)** : Dépend de la Phase 4 — refactorise en parallèle `extract_parent_contacts.py` (`T017`) et `generate_contacts_vcf.py` (`T018`) et vérifie la non-duplication (`T016`).
- **Polish (Phase 6)** : Dépend de la Phase 5 — met à jour `README.md` (`T019`) et exécute la validation finale (`T020`).

### User Story Dependencies

- **User Story 1 (P1 - Domaine)** : Dépend uniquement de la Phase 2 (Foundational). Peut être testée de façon autonome dès la fin de la Phase 3.
- **User Story 2 (P1 - Parseurs & Exporteurs en mémoire/disque)** : Utilise les entités et fonctions de `sgdf_contacts.domain` (US1). Peut être testée de façon autonome dès la fin de la Phase 4.
- **User Story 3 (P1 - Rétrocompatibilité CLI)** : Connecte les scripts CLI `extract_parent_contacts.py` et `generate_contacts_vcf.py` aux modules de US1 et US2.

### Parallel Opportunities

- En Phase 2 : `T003` (`constants.py`) et `T004` (`exceptions.py`) sont exécutables en parallèle.
- En Phase 3 (US1) : `T005` (`test_sgdf_contacts_package.py`) et `T006` (`normalization.py`) sont exécutables en parallèle.
- En Phase 4 (US2) : `T010` (`individuals_xls.py`), `T011` (`parents_excel.py`), `T013` (`excel.py`) et `T014` (`vcard.py`) portent sur quatre fichiers distincts et sont exécutables en parallèle.
- En Phase 5 (US3) : `T016` (`test_sgdf_contacts_package.py`), `T017` (`extract_parent_contacts.py`) et `T018` (`generate_contacts_vcf.py`) portent sur trois fichiers distincts et sont exécutables en parallèle.

---

## Parallel Example: User Story 2 & User Story 3

```bash
# En Phase 4 (US2), lancement parallèle des parseurs et exporteurs sur fichiers distincts :
Task: "T010 [P] [US2] Implémenter read_individuals_export_table et extract_and_group_parents dans sgdf_contacts/parsers/individuals_xls.py"
Task: "T011 [P] [US2] Implémenter read_parent_contacts_excel dans sgdf_contacts/parsers/parents_excel.py"
Task: "T013 [P] [US2] Implémenter write_parent_contacts_workbook dans sgdf_contacts/exporters/excel.py"
Task: "T014 [P] [US2] Implémenter format_parent_vcard et write_vcf_file dans sgdf_contacts/exporters/vcard.py"

# En Phase 5 (US3), refactorisation parallèle des deux points d'entrée CLI :
Task: "T017 [P] [US3] Refactoriser extract_parent_contacts.py"
Task: "T018 [P] [US3] Refactoriser generate_contacts_vcf.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Compléter Phase 1 (`T001`, `T002`) et Phase 2 (`T003`, `T004`)
2. Compléter Phase 3 (`T005` à `T008` — US1 : cœur métier pur `sgdf_contacts.domain` avec `waha_chat_id`)
3. **STOP et VALIDATION** : Vérifier les tests unitaires du domaine dans `tests/test_sgdf_contacts_package.py`

### Incremental Delivery

1. Ajouter Phase 4 (`T009` à `T015` — US2 : parseurs `bytes`/`Path` et exporteurs `BytesIO`/vCard direct depuis `list[ParentContact]`) → Tester indépendamment
2. Ajouter Phase 5 (`T016` à `T018` — US3 : délégation depuis `extract_parent_contacts.py` et `generate_contacts_vcf.py` sans duplication) → Tester toute la suite existante
3. Compléter Phase 6 (`T019`, `T020` — documentation `README.md`, `pytest -v` et `ruff check .`)
