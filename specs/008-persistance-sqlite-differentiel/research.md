# Research: Persistance Locale des Contacts Parents et Calcul de Différentiel d'Import

**Feature**: `008-persistance-sqlite-differentiel` | **Date**: 2026-10-26

## Decision 1: Choix de l'ORM et déclaration dans l'environnement éphémère (`flake.nix` & `devbox.json`)

- **Decision**: Utiliser `sqlmodel` (qui embarque et expose `sqlalchemy` 2.x et `pydantic`) en l'ajoutant avec `sqlalchemy` dans `flake.nix` (`python3.withPackages`) et `devbox.json` (`python3Packages.sqlmodel@latest` et `python3Packages.sqlalchemy@latest`), sans introduire `alembic` à ce stade.
- **Rationale**:
  - Dans le registre Nix verrouillé du projet (`flake.lock`), `python3Packages.sqlmodel` (v0.0.42) et `python3Packages.sqlalchemy` (v2.0.51) sont directement disponibles sans compilation.
  - `SQLModel.metadata.create_all(engine)` suffit pour initialiser de manière idempotente le schéma des 3 tables (`parents`, `children`, `parent_child_links`) sur SQLite (et reste 100 % compatible PostgreSQL).
  - Éviter `alembic` tant qu'aucune migration de base en production n'est requise respecte le Principe V (Simplicité et Maintenabilité — YAGNI) de la constitution.
- **Alternatives considered**:
  - *`sqlite3` standard pur* : Écarté car l'issue #4 exige explicitement SQLModel / SQLAlchemy pour garantir la compatibilité PostgreSQL et disposer d'un modèle typé.
  - *Ajout d'Alembic dès maintenant* : Écarté car superflu pour la création initiale et l'utilisation locale SQLite.

## Decision 2: Configuration automatique de SQLite (`PRAGMA journal_mode=WAL;` et `PRAGMA foreign_keys=ON;`)

- **Decision**: Attacher un écouteur d'événement SQLAlchemy `@event.listens_for(engine, "connect")` lors de la création du moteur (`create_sqlite_engine` / `init_db`) qui exécute systématiquement `PRAGMA foreign_keys=ON;` et `PRAGMA journal_mode=WAL;` lorsque le dialecte est SQLite.
- **Rationale**:
  - SQLite désactive `foreign_keys` par défaut à chaque nouvelle connexion ; l'événement `connect` garantit que chaque connexion du pool applique immédiatement les deux pragmas.
  - Si un moteur non-SQLite (ex. PostgreSQL) est fourni dans le futur, la vérification du dialecte (`connection.engine.dialect.name == "sqlite"` ou via l'URL) évite d'exécuter des pragmas spécifiques à SQLite.
- **Alternatives considered**:
  - *Exécuter les pragmas une seule fois dans `init_db()`* : Insuffisant pour `PRAGMA foreign_keys=ON;`, qui est propre à chaque connexion SQLite et non persistant dans le fichier de base.

## Decision 3: Schéma relationnel et préservation de l'ordre des enfants (`parents`, `children`, `parent_child_links`)

- **Decision**: Définir trois modèles `SQLModel(..., table=True)` dans `sgdf_contacts/persistence/models.py` :
  1. `ParentChildLink` (`table_name="parent_child_links"`) : table de liaison N-N avec clés primaires composites `(parent_id, child_id)` et une colonne `position: int = 0` permettant de restituer les enfants rattachés à un parent dans leur ordre exact d'apparition lors de l'extraction.
  2. `ParentRecord` (`table_name="parents"`) : `id`, `member_id`, `last_name`, `first_name`, `primary_mobile_phone`, `secondary_mobile_phone`, `landline_phone`, `email_address`, `street`, `postal_code`, `city`, `notes`, `has_whatsapp` (`bool | None = None`), `first_seen_at` (`datetime`), `updated_at` (`datetime`), `is_active` (`bool = True`), ainsi qu'une méthode `to_domain() -> ParentContact` qui reconstruit fidèlement l'entité `ParentContact` du domaine.
  3. `ChildRecord` (`table_name="children"`) : `id`, `first_name`, `last_name`, `short_unit`, `registration_status`, avec unicité logique sur `(last_name, first_name)` et méthode `to_domain() -> AttachedChild`.
- **Rationale**:
  - La colonne `position` sur `parent_child_links` (ou le maintien de l'ordre de rattachement) garantit que la reconversion `ParentRecord.to_domain()` produit exactement les mêmes chaînes `children_names` (`Enfants`), `children_units` (`Unités`) et notes vCard que l'extraction directe depuis `ExportIndividus.xls`.
  - Stocker `notes` consolidées sur `ParentRecord` (et reconstruire `notes_list = [n for n in notes.split(" ; ") if n]` dans `to_domain()`) assure une bijection parfaite entre `ParentContact` et `ParentRecord`.
- **Alternatives considered**:
  - *Ne pas stocker la position du lien parent-enfant* : Risquerait d'inverser l'ordre d'affichage d'une fratrie lors de la relecture en base et de créer de faux positifs ou des écarts de formatage dans `ContactParents.vcf` et `ContactsParents.xlsx`.

## Decision 4: Algorithme de réconciliation et calcul de différentiel (`ImportDiffReport`)

- **Decision**: Dans `ParentContactRepository` (`sgdf_contacts/persistence/repository.py`), implémenter l'import transactionnel (`upsert_parents` et `import_from_individuals_xls`) selon les règles suivantes :
  1. **Clé de réconciliation d'un parent** :
     - Si le `ParentContact` entrant possède un `member_id` non vide et qu'un `ParentRecord` en base possède déjà ce `member_id`, les associer.
     - Sinon, rechercher un `ParentRecord` existant par le couple `(last_name, first_name)`.
  2. **Comparaison champ par champ pour détecter les modifications (`updated` vs `unchanged`)** :
     - Comparer les champs métier suivants entre l'état en base avant import et le `ParentContact` entrant :
       `member_id`, `last_name`, `first_name`, `primary_mobile_phone`, `secondary_mobile_phone`, `landline_phone`, `email_address`, `street`, `postal_code`, `city`, `notes`, `children_names`, `children_units`, `children_statuses` (ou la liste ordonnée des tuples `(first_name, last_name, short_unit, registration_status)` des enfants), ainsi que `is_active` (si le parent était désactivé `is_active=False` et redevient actif `is_active=True`).
     - Si aucune différence n'est constatée, le parent est ajouté à `report.unchanged` et son `updated_at` n'est pas modifié.
     - Si au moins un champ diffère, mettre à jour les colonnes et les liens enfants, rafraîchir `updated_at`, conserver `first_seen_at` et `has_whatsapp` intacts, et ajouter une entrée `ParentUpdateDiff(parent=..., changes={"field": FieldChange(old=..., new=...)})` dans `report.updated`.
  3. **Désactivation douce (`deactivated`)** :
     - Tout `ParentRecord` qui était actif (`is_active == True`) avant l'import et qui n'a été associé à aucun parent du nouvel export passe à `is_active = False` (avec mise à jour de `updated_at`, tout en conservant `has_whatsapp` et `first_seen_at`) et est ajouté à `report.deactivated`.
- **Rationale**:
  - Garantit une idempotence stricte (`0 created`, `0 updated`, `0 deactivated` lors d'un second import identique).
  - Préserve les métadonnées externes (`has_whatsapp`) aussi bien lors des mises à jour que lors des désactivations temporaires ou définitives.
- **Alternatives considered**:
  - *Suppression physique (`DELETE`) des parents absents* : Contraire à l'exigence de l'issue #4 qui impose `is_active = False` sans suppression brutale des métadonnées externes comme `has_whatsapp`.

## Decision 5: Régénération directe de `ContactParents.vcf` et `ContactsParents.xlsx` depuis SQLite

- **Decision**: Fournir dans `ParentContactRepository` (et via des fonctions de haut niveau dans `sgdf_contacts/persistence`) :
  - `list_active_parents() -> list[ParentContact]` : retourne les entités `ParentContact` actives triées avec `parent_sort_key` (tri alphabétique français sans accents ni casse).
  - `export_vcf_from_db(output_path: Path | None = None) -> str` : s'appuie sur `write_vcf_file(output_path, repository.list_active_parents())`.
  - `export_excel_from_db(output_path: Path | BinaryIO | None = None) -> bytes` : s'appuie sur `write_parent_contacts_workbook(output_path=output_path, parent_contacts=repository.list_active_parents())`.
- **Rationale**:
  - Réutilise 100 % des exporteurs existants (`sgdf_contacts.exporters.vcard` et `sgdf_contacts.exporters.excel`) sans dupliquer aucune logique de formatage Excel ou vCard.
- **Alternatives considered**:
  - *Écrire des générateurs dédiés à la base de données* : Violait le principe DRY et le Principe V de la constitution.
