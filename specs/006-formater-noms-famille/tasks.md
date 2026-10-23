---

description: "Liste des tâches pour le formatage des noms de famille en casse titre comme les prénoms"
---

# Tasks: Formatage des Noms de Famille en Casse Titre Comme les Prénoms

**Input**: Documents de conception depuis `/specs/006-formater-noms-famille/`

**Prerequisites**: `plan.md` (requis), `spec.md` (requis pour les récits utilisateurs), `research.md`, `data-model.md`, `contracts/contrat-formatage-noms.md`, `quickstart.md`

**Tests**: Inclus conformément à `spec.md` (`SC-004`) et `plan.md` (`tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) pour valider unitairement et de bout en bout les 2 User Stories sans exposer de données personnelles.

**Organization**: Les tâches sont organisées par récit utilisateur (User Story) afin que chaque incrément puisse être implémenté et testé indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Exécutable en parallèle (fichiers distincts, aucune dépendance sur une tâche inachevée)
- **[Story]**: Récit utilisateur auquel appartient la tâche (`[US1]`, `[US2]`)
- Chaque description inclut le chemin exact du fichier concerné

## Path Conventions

- **Script d'extraction Excel** : `extract_parent_contacts.py`
- **Script de génération vCard** : `generate_contacts_vcf.py`
- **Tests automatisés** : `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`
- **Documentation** : `README.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Vérification initiale de l'environnement éphémère Python 3 avant modification

- [X] T001 Vérifier le bon fonctionnement de l'environnement éphémère en exécutant la suite de tests d'environnement dans `tests/test_environment.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Mise à jour de la fonction centrale de normalisation des noms de famille utilisée par toute la chaîne d'extraction, de regroupement et d'export

**⚠️ CRITICAL**: Ce socle est requis par toutes les User Stories

- [X] T002 Mettre à jour la fonction `normalize_last_name(raw_last_name: str) -> str` pour appliquer la casse titre comme `normalize_first_name` (contraintes de `data-model.md` : `"1. Suppression des espaces en début/fin et réduction des espaces multiples internes à un seul espace."`, `"2. Conversion de tous les caractères en minuscules."`, `"3. Conversion en majuscule de la première lettre située en début de chaîne ou immédiatement après un espace ( ), un trait d'union (-) ou une apostrophe (')."`) dans `extract_parent_contacts.py`

**Checkpoint**: La fonction `normalize_last_name` formate désormais tous les noms de famille en minuscules avec la première lettre de chaque mot/segment en majuscule.

---

## Phase 3: User Story 1 - Formatage des noms de famille des parents et des enfants comme les prénoms lors de l'extraction (Priority: P1) 🎯 MVP

**Goal**: Formater tous les noms de famille des parents (colonne `Nom`), des enfants (colonne `Noms des enfants` sous la forme `Prénom Nom`) et des profils adultes en casse titre lors de l'extraction vers `ContactsParents.xlsx`, tout en conservant le dédoublonnage, l'enrichissement adulte, le tri alphabétique français et l'onglet brut `ExportIndividus` intact.

**Independent Test**: Exécuter `pytest tests/test_extract_parent_contacts.py` pour vérifier sur données synthétiques et réelles que les noms simples, composés, à espaces, avec apostrophe ou accentués sont tous formatés en casse titre dans l'onglet `ContactsParents`.

### Tests for User Story 1

- [X] T003 [P] [US1] Mettre à jour les tests unitaires et d'intégration d'extraction (`test_normalization_names_phones_units_and_addresses`, `test_sibling_deduplication_enrichment_and_alphabetical_sorting`, `test_excel_workbook_generation_and_cli`, `test_real_individuals_export_integration`) avec les attentes en casse titre (`Dupont-Moretti`, `Le Goff`, `D'Artagnan`, `Bernard`, `Évrard`, `Zimmer`, `Lucas Bernard, Chloé Bernard`, `Tom Martin`, `Léa Dupont`) et les commentaires associés dans `tests/test_extract_parent_contacts.py`

### Implementation for User Story 1

- [X] T004 [US1] Mettre à jour les docstrings de `AttachedChild.format_full_name` et `ParentContact.children_names` conformément à `data-model.md` (`"Casse titre (Bernard)"` pour `last_name`, `"Prénom Nom (Lucas Bernard)"` pour `format_full_name()`, `"Lucas Bernard, Chloé Bernard"` pour `children_names`) dans `extract_parent_contacts.py`

**Checkpoint**: L'extraction vers `ContactsParents.xlsx` (US1) produit tous les noms de famille des parents et des enfants en casse titre et passe 100 % des tests de `tests/test_extract_parent_contacts.py`.

---

## Phase 4: User Story 2 - Cohérence des noms de famille dans le fichier d'import Google Contacts (`ContactParents.vcf`) et la documentation (Priority: P1)

**Goal**: Restituer le format `Prénom Nom` dans les propriétés `N`, `FN` et `NOTE` (`Enfants : Prénom Nom (Unité)`) de `ContactParents.vcf` et mettre à jour la documentation `README.md` ainsi que les docstrings et les tests de génération vCard.

**Independent Test**: Exécuter `pytest tests/test_generate_contacts_vcf.py` et inspecter `README.md` pour vérifier que toutes les fiches vCard et la documentation reflètent le format `Prénom Nom`.

### Tests for User Story 2

- [X] T005 [P] [US2] Mettre à jour les tests unitaires et d'intégration de génération vCard (`test_vcard_escaping_and_direct_address_assignment`, `test_format_children_with_units_and_build_note`, `test_parent_vcard_serialization_complete_and_partial`, `test_vcf_file_generation_via_cli`, `test_real_contacts_parents_xlsx_integration`) pour vérifier les valeurs en casse titre (contraintes de `data-model.md` : `"N:Dupont;Jean-Pierre;;;"` pour `N`, `"FN:Jean-Pierre Dupont"` pour `FN`, `"Enfants : Lucas Bernard (Scouts-Guides), Chloé Bernard (Farfadets)"` pour `NOTE`) dans `tests/test_generate_contacts_vcf.py`

### Implementation for User Story 2

- [X] T006 [P] [US2] Mettre à jour les docstrings du module, de `ParentContactCard.formatted_full_name` et de `format_children_with_units` pour mentionner le format `Prénom Nom` dans `generate_contacts_vcf.py`
- [X] T007 [P] [US2] Mettre à jour la documentation des colonnes `Nom` et `Noms des enfants` de l'onglet `ContactsParents` et des champs `Identité` et `Informations complémentaires (NOTE)` de `ContactParents.vcf` (exemples `Prénom Nom`, `Lucas Bernard, Chloé Bernard`) dans `README.md`

**Checkpoint**: Les deux User Stories (US1 et US2) sont complètes et vérifiables indépendamment.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Régénération de bout en bout des fichiers locaux (si `ExportIndividus.xls` est présent) et validation finale de la qualité du code et des tests

- [X] T008 Exécuter le flux complet de bout en bout (`extract_parent_contacts.py` puis `generate_contacts_vcf.py` si `ExportIndividus.xls` est présent), puis lancer `ruff check .` et `pytest -v` conformément au guide de validation `specs/006-formater-noms-famille/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** : Aucune dépendance — démarre immédiatement (`T001`).
- **Foundational (Phase 2)** : Dépend de la Phase 1 — met à jour `normalize_last_name` dans `extract_parent_contacts.py` (`T002`).
- **User Story 1 (Phase 3 - P1)** : Dépend de la Phase 2 — met à jour les tests d'extraction (`T003`) et les docstrings dans `extract_parent_contacts.py` (`T004`).
- **User Story 2 (Phase 4 - P1)** : Dépend de la Phase 2 — met à jour en parallèle `tests/test_generate_contacts_vcf.py` (`T005`), `generate_contacts_vcf.py` (`T006`) et `README.md` (`T007`).
- **Polish (Phase 5)** : Dépend des Phases 3 et 4 (`T008`).

### User Story Dependencies

- **User Story 1 (P1)** : Dépend uniquement de la tâche fondatrice `T002`.
- **User Story 2 (P1)** : Dépend de la tâche fondatrice `T002` (et de l'exécution d'extraction pour le test sur le fichier `ContactsParents.xlsx` réel en Phase 5) ; ses tâches `T005`, `T006` et `T007` portent sur des fichiers distincts de US1 et peuvent être réalisées en parallèle.

### Parallel Opportunities

- `T003` (`tests/test_extract_parent_contacts.py`), `T005` (`tests/test_generate_contacts_vcf.py`), `T006` (`generate_contacts_vcf.py`) et `T007` (`README.md`) portent sur quatre fichiers distincts et peuvent être exécutées en parallèle dès que `T002` est terminée.

---

## Parallel Example: User Story 1 & User Story 2

```bash
# Exécution en parallèle sur fichiers distincts après T002 :
Task: "T003 [P] [US1] Mettre à jour les tests d'extraction dans tests/test_extract_parent_contacts.py"
Task: "T005 [P] [US2] Mettre à jour les tests vCard dans tests/test_generate_contacts_vcf.py"
Task: "T006 [P] [US2] Mettre à jour les docstrings dans generate_contacts_vcf.py"
Task: "T007 [P] [US2] Mettre à jour la documentation dans README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Compléter Phase 1 (`T001`) et Phase 2 (`T002`)
2. Compléter Phase 3 (`T003`, `T004` — US1 : noms de famille des parents et des enfants en casse titre lors de l'extraction)
3. **STOP et VALIDATION** : Vérifier `pytest tests/test_extract_parent_contacts.py`

### Incremental Delivery

1. Ajouter Phase 4 (`T005`, `T006`, `T007` — US2 : cohérence dans `ContactParents.vcf`, ses tests et `README.md`)
2. Compléter Phase 5 (`T008` — régénération de bout en bout, `ruff check .` et `pytest -v`)
