---

description: "Task list for SQLite persistence and differential import calculation"
---

# Tasks: Persistance Locale des Contacts Parents et Calcul de Différentiel d'Import

**Input**: Design documents from `/specs/008-persistance-sqlite-differentiel/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/contrat-persistance.md, quickstart.md

**Tests**: Inclus conformément aux critères d'acceptation de l'issue #4 et à la spécification (`tests/test_environment.py` et `tests/test_persistence.py`).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Package & CLI**: `sgdf_contacts/`, `tests/`, `flake.nix`, `devbox.json`, `.gitignore`, `README.md` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Déclaration des dépendances `sqlmodel` et `sqlalchemy` dans l'environnement éphémère Nix/Devbox, protection RGPD des bases SQLite dans `.gitignore`, et création de l'arborescence `sgdf_contacts/persistence/`.

- [X] T001 [P] Ajouter `sqlmodel` et `sqlalchemy` dans `python3.withPackages` et dans le message `shellHook` de `flake.nix`
- [X] T002 [P] Ajouter `python3Packages.sqlmodel@latest` et `python3Packages.sqlalchemy@latest` en parité stricte (ainsi que dans `init_hook` et `check_environment`) dans `devbox.json`
- [X] T003 [P] Ajouter les motifs d'exclusion des fichiers SQLite locaux (`*.db`, `*.sqlite`, `*.sqlite3`, `*-wal`, `*-shm`) dans `.gitignore`
- [X] T004 [P] Mettre à jour `REQUIRED_PYTHON_MODULES`, `EXPECTED_NIX_PACKAGES` et `test_gitignore_data_protection` dans `tests/test_environment.py` pour vérifier `sqlmodel`, `sqlalchemy` et `*.db`
- [X] T005 Créer le répertoire du sous-package `sgdf_contacts/persistence/` avec un fichier d'initialisation `sgdf_contacts/persistence/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modèles SQLModel (`parents`, `children`, `parent_child_links`), contraintes SQL, configuration automatique des pragmas SQLite (`WAL` et `foreign_keys`) et initialisation du schéma.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implémenter `ParentChildLink` (`__tablename__ = "parent_child_links"`) avec `parent_id: int | None` (`PRIMARY KEY`, `FOREIGN KEY(parents.id)`), `child_id: int | None` (`PRIMARY KEY`, `FOREIGN KEY(children.id)`) et `position: int = 0` (`NOT NULL DEFAULT 0`) dans `sgdf_contacts/persistence/models.py`
- [X] T007 Implémenter `ChildRecord` (`__tablename__ = "children"`) avec `id: int | None` (`PRIMARY KEY AUTOINCREMENT`), `first_name: str` (`NOT NULL`, indexé), `last_name: str` (`NOT NULL`, indexé), `short_unit: str` (`NOT NULL DEFAULT ''`, indexé), `registration_status: str` (`NOT NULL DEFAULT ''`, indexé), contrainte `UniqueConstraint("last_name", "first_name", name="uq_children_last_first_name")` et méthode `to_domain() -> AttachedChild` dans `sgdf_contacts/persistence/models.py`
- [X] T008 Implémenter `ParentRecord` (`__tablename__ = "parents"`) avec `id: int | None` (`PRIMARY KEY AUTOINCREMENT`), `member_id: str` (`NOT NULL DEFAULT ''`, indexé), `last_name: str` (`NOT NULL`, indexé), `first_name: str` (`NOT NULL`, indexé), `primary_mobile_phone: str` (`NOT NULL DEFAULT ''`, indexé), `secondary_mobile_phone: str` (`NOT NULL DEFAULT ''`, indexé), `landline_phone: str` (`NOT NULL DEFAULT ''`, indexé), `email_address: str` (`NOT NULL DEFAULT ''`), `street: str` (`NOT NULL DEFAULT ''`), `postal_code: str` (`NOT NULL DEFAULT ''`), `city: str` (`NOT NULL DEFAULT ''`), `notes: str` (`NOT NULL DEFAULT ''`), `has_whatsapp: bool | None` (`NULL DEFAULT NULL`), `first_seen_at: datetime` (`NOT NULL`), `updated_at: datetime` (`NOT NULL`), `is_active: bool` (`NOT NULL DEFAULT True`, indexé), contrainte `UniqueConstraint("last_name", "first_name", name="uq_parents_last_first_name")` et méthode `to_domain()` dans `sgdf_contacts/persistence/models.py`
- [X] T009 Implémenter `create_db_engine(database_url: str | Path = "sqlite:///sgdf_contacts.db", *, echo: bool = False) -> Engine` (activant automatiquement `PRAGMA journal_mode=WAL;` et `PRAGMA foreign_keys=ON;` via un écouteur `@event.listens_for(engine, "connect")` sur SQLite) ainsi que `init_db(engine: Engine) -> None` dans `sgdf_contacts/persistence/models.py`

**Checkpoint**: Le moteur SQLite/SQLModel et les 3 tables relationnelles sont prêts pour l'implémentation des User Stories.

---

## Phase 3: User Story 1 - Stockage persistant des parents et de leurs enfants avec calcul automatique des nouveautés et modifications à chaque import (Priority: P1) 🎯 MVP

**Goal**: Synchroniser de manière transactionnelle les parents et leurs enfants dans SQLite à partir d'une liste de `ParentContact` ou directement d'un export `ExportIndividus.xls`, réconcilier sur `member_id` ou `(last_name, first_name)`, désactiver sans supprimer les parents absents (`is_active = False` en conservant `has_whatsapp`), et retourner un rapport détaillé `ImportDiffReport` (`created`, `updated`, `unchanged`, `deactivated`).

**Independent Test**: Initialiser une base SQLite temporaire, importer `ExportIndividus.xls` une première fois (`134 created`, `0 updated`), ré-importer le même fichier (`0 created`, `0 updated`, `134 unchanged`), puis importer un jeu modifié (création, modification de coordonnées/enfants, retrait d'un parent ayant `has_whatsapp=True`) et vérifier le contenu exact de `ImportDiffReport` ainsi que la préservation de `has_whatsapp`.

### Implementation for User Story 1

- [X] T010 [US1] Définir les structures de rapport `FieldChange` (`old_value`, `new_value`), `ParentUpdateDiff` (`parent`, `changes: dict[str, FieldChange]`) et `ImportDiffReport` (`created`, `updated`, `unchanged`, `deactivated`) dans `sgdf_contacts/persistence/repository.py`
- [X] T011 [US1] Implémenter dans `ParentContactRepository` (`sgdf_contacts/persistence/repository.py`) la méthode transactionnelle `sync_parents(self, parents: Sequence[ParentContact]) -> ImportDiffReport` gérant la réconciliation par `member_id` ou `(last_name, first_name)`, l'upsert des `ChildRecord` et des liens ordonnés `ParentChildLink`, le calcul champ par champ des modifications, la désactivation douce (`is_active = False`) des parents absents et la préservation de `has_whatsapp` et `first_seen_at`
- [X] T012 [US1] Implémenter dans `ParentContactRepository` (`sgdf_contacts/persistence/repository.py`) les méthodes `import_individuals_xls(self, source: Path | bytes | BinaryIO) -> ImportDiffReport` et `set_whatsapp_status(self, last_name: str, first_name: str, has_whatsapp: bool | None) -> bool`
- [X] T013 [US1] Écrire les tests unitaires et d'intégration de la User Story 1 (pragmas `WAL` et `foreign_keys`, import initial, idempotence stricte au ré-import, détection fine des `created`/`updated`/`unchanged`/`deactivated`, réactivation d'un parent inactif et préservation de `has_whatsapp`) dans `tests/test_persistence.py`

**Checkpoint**: User Story 1 est fonctionnelle et testable indépendamment (MVP de persistance et différentiel d'import).

---

## Phase 4: User Story 2 - Consultation, filtrage et recherche rapide des parents stockés (Priority: P1)

**Goal**: Interroger directement la base SQLite pour lister les parents actifs selon le tri alphabétique français, filtrer par unité courte d'enfant (`short_unit`), par statut d'inscription (`registration_status`) ou par présence d'un numéro de portable valide, et rechercher un parent par numéro de téléphone (`primary_mobile_phone`, `secondary_mobile_phone`, `landline_phone`).

**Independent Test**: Sur une base SQLite alimentée, vérifier que `list_active_parents()` retourne uniquement les parents actifs triés selon `parent_sort_key`, que `filter_parents(...)` filtre exactement par unité, statut d'inscription et portable valide, et que `find_by_phone(...)` retrouve un parent à partir de n'importe lequel de ses trois numéros (brut ou normalisé).

### Implementation for User Story 2

- [X] T014 [US2] Implémenter `list_active_parents(self) -> list[ParentContact]` et `filter_parents(self, *, short_unit: str | None = None, registration_status: str | None = None, has_valid_mobile: bool | None = None, include_inactive: bool = False) -> list[ParentContact]` avec tri alphabétique français dans `sgdf_contacts/persistence/repository.py`
- [X] T015 [US2] Implémenter `find_by_phone(self, phone: str, *, include_inactive: bool = False) -> ParentContact | None` recherchant sur `primary_mobile_phone`, `secondary_mobile_phone` et `landline_phone` (avec normalisation automatique du numéro cherché) dans `sgdf_contacts/persistence/repository.py`
- [X] T016 [US2] Ajouter les tests unitaires de listage trié, de filtrage multicritère (`short_unit`, `registration_status`, `has_valid_mobile`, exclusion des inactifs par défaut) et de recherche par téléphone sur les 3 champs dans `tests/test_persistence.py`

**Checkpoint**: User Stories 1 et 2 fonctionnent et sont testées indépendamment.

---

## Phase 5: User Story 3 - Régénération directe des fichiers d'export (`ContactParents.vcf` et `ContactsParents.xlsx`) depuis le stockage local (Priority: P1)

**Goal**: Régénérer `ContactParents.vcf` et `ContactsParents.xlsx` directement à partir des parents actifs stockés dans la base SQLite sans relire le fichier `ExportIndividus.xls`.

**Independent Test**: Importer `ExportIndividus.xls` dans une base SQLite temporaire, appeler `repo.export_vcf(...)` et `repo.export_excel(...)` sans fournir `ExportIndividus.xls`, et vérifier que le contenu `.vcf` et les 134 lignes de l'onglet `ContactsParents` dans `.xlsx` sont strictement identiques à ceux générés directement depuis `ExportIndividus.xls`.

### Implementation for User Story 3

- [X] T017 [US3] Implémenter `export_vcf(self, output_path: Path | None = None, *, categories: tuple[str, ...] = DEFAULT_CATEGORIES) -> str` et `export_excel(self, output_path: Path | BinaryIO | None = None, *, source_headers: list[str] | None = None, source_rows: list[list[str]] | None = None) -> bytes` dans `sgdf_contacts/persistence/repository.py`
- [X] T018 [US3] Exporter publiquement `ParentRecord`, `ChildRecord`, `ParentChildLink`, `FieldChange`, `ParentUpdateDiff`, `ImportDiffReport`, `ParentContactRepository`, `create_db_engine` et `init_db` dans `sgdf_contacts/persistence/__init__.py` et `sgdf_contacts/__init__.py`
- [X] T019 [US3] Ajouter dans `tests/test_persistence.py` les tests d'intégration vérifiant que `ContactParents.vcf` et `ContactsParents.xlsx` régénérés depuis la base SQLite (y compris sur les 134 parents de `ExportIndividus.xls`) sont strictement identiques aux exports directs

**Checkpoint**: Toutes les User Stories (US1, US2, US3) sont complètes et vérifiées.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation en français dans `README.md`, validation complète des tests et de `ruff`, commit et ouverture de la Pull Request avec un titre en anglais via `gh`.

- [X] T020 [P] Mettre à jour `README.md` en français pour documenter le sous-package `sgdf_contacts.persistence` (modèles SQLite/SQLModel, import avec calcul de différentiel `ImportDiffReport`, requêtage et régénération `.vcf`/`.xlsx` depuis SQLite)
- [X] T021 Exécuter la validation de bout en bout (`pytest` et `ruff check .`) dans l'environnement éphémère Nix conformément à `specs/008-persistance-sqlite-differentiel/quickstart.md`
- [X] T022 Valider les modifications sur la branche `008-persistance-sqlite-differentiel`, pousser la branche sur `origin` et créer la Pull Request avec un titre en anglais via `gh pr create` (sans la fusionner)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1 : T001–T005)**: Aucune dépendance — démarre immédiatement. T001, T002, T003 et T004 sont parallélisables.
- **Foundational (Phase 2 : T006–T009)**: Dépend de la Phase 1 — bloque toutes les User Stories.
- **User Story 1 (Phase 3 : T010–T013)**: Dépend de la Phase 2.
- **User Story 2 (Phase 4 : T014–T016)**: Dépend de la Phase 2 et s'intègre dans `ParentContactRepository` (T011).
- **User Story 3 (Phase 5 : T017–T019)**: Dépend de `list_active_parents` (T014).
- **Polish (Phase 6 : T020–T022)**: Dépend de la complétion des Phases 3, 4 et 5.

### User Story Dependencies

- **User Story 1 (P1 - MVP)**: Stockage SQLite et calcul de différentiel `ImportDiffReport`.
- **User Story 2 (P1)**: Requêtage, filtrage et recherche par téléphone sur les enregistrements persistés par US1.
- **User Story 3 (P1)**: Régénération directe des exports `.vcf` et `.xlsx` à partir de `list_active_parents()` de US2.

### Parallel Opportunities

- En Phase 1 : `T001` (`flake.nix`), `T002` (`devbox.json`), `T003` (`.gitignore`) et `T004` (`tests/test_environment.py`) portent sur des fichiers distincts et peuvent être exécutés en parallèle.
- En Phase 6 : `T020` (`README.md`) peut être rédigé parallèlement aux dernières vérifications de `tests/test_persistence.py`.

---

## Parallel Example: Setup Phase

```bash
# Exécution parallèle des mises à jour d'environnement et de protection Git :
Task T001: "Ajouter sqlmodel et sqlalchemy dans flake.nix"
Task T002: "Ajouter python3Packages.sqlmodel@latest et python3Packages.sqlalchemy@latest dans devbox.json"
Task T003: "Ajouter les motifs *.db, *.sqlite, *.sqlite3, *-wal, *-shm dans .gitignore"
Task T004: "Mettre à jour tests/test_environment.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Compléter Phase 1 (Setup Nix/Devbox/`.gitignore`) et Phase 2 (`sgdf_contacts/persistence/models.py`).
2. Compléter Phase 3 (User Story 1 : `sync_parents`, `import_individuals_xls`, `ImportDiffReport` et tests d'idempotence/différentiel).
3. **STOP & VALIDATE** : Vérifier que l'import et le calcul de différentiel sur base SQLite temporaire passent à 100 %.

### Incremental Delivery

1. Setup + Foundational → Moteur SQLite WAL + modèles `SQLModel` prêts.
2. User Story 1 → Upsert transactionnel et `ImportDiffReport` validés.
3. User Story 2 → Requêtage trié, filtres par unité/statut/portable et recherche par téléphone validés.
4. User Story 3 → Régénération directe de `ContactParents.vcf` et `ContactsParents.xlsx` depuis SQLite validée.
5. Polish → Mise à jour de `README.md`, validation complète `pytest` + `ruff`, commit et création de la Pull Request avec un titre en anglais.
