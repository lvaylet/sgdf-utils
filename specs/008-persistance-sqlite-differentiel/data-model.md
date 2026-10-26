# Data Model: Persistance SQLite (`SQLModel`) et Calcul de Différentiel

**Feature**: `008-persistance-sqlite-differentiel` | **Date**: 2026-10-26

## 1. Modèles de Base de Données (`sgdf_contacts/persistence/models.py`)

### 1.1 `ParentChildLink` (Table `parent_child_links`)

Table de liaison plusieurs-à-plusieurs (`N-N`) entre `parents` et `children`, conservant l'ordre d'apparition des enfants rattachés à un parent.

| Champ | Type Python / SQLModel | Contraintes SQL | Description |
|-------|------------------------|-----------------|-------------|
| `parent_id` | `int | None` | `PRIMARY KEY`, `FOREIGN KEY(parents.id) ON DELETE CASCADE` | Identifiant du parent rattaché |
| `child_id` | `int | None` | `PRIMARY KEY`, `FOREIGN KEY(children.id) ON DELETE CASCADE` | Identifiant de l'enfant rattaché |
| `position` | `int` | `NOT NULL DEFAULT 0` | Position d'ordre de l'enfant dans la liste du parent |

---

### 1.2 `ParentRecord` (Table `parents`)

Enregistrement persistant d'un parent de jeune(s) scout(s) SGDF.

| Champ | Type Python / SQLModel | Contraintes SQL | Description |
|-------|------------------------|-----------------|-------------|
| `id` | `int | None` | `PRIMARY KEY AUTOINCREMENT` | Identifiant technique unique |
| `member_id` | `str` | `NOT NULL DEFAULT ''`, indexé | Numéro d'adhérent SGDF du parent (si inscrit comme adulte) |
| `last_name` | `str` | `NOT NULL`, indexé | Nom de famille normalisé (ex. `"Martin"`) |
| `first_name` | `str` | `NOT NULL`, indexé | Prénom normalisé (ex. `"Jean-Pierre"`) |
| `primary_mobile_phone` | `str` | `NOT NULL DEFAULT ''`, indexé | Téléphone portable principal normalisé (`+336...` / `+337...`) |
| `secondary_mobile_phone` | `str` | `NOT NULL DEFAULT ''`, indexé | Téléphone portable secondaire normalisé |
| `landline_phone` | `str` | `NOT NULL DEFAULT ''`, indexé | Téléphone fixe ou autre numéro normalisé |
| `email_address` | `str` | `NOT NULL DEFAULT ''` | Adresse courriel normalisée en minuscules |
| `street` | `str` | `NOT NULL DEFAULT ''` | Rue normalisée |
| `postal_code` | `str` | `NOT NULL DEFAULT ''` | Code postal normalisé |
| `city` | `str` | `NOT NULL DEFAULT ''` | Ville normalisée |
| `notes` | `str` | `NOT NULL DEFAULT ''` | Remarques consolidées séparées par `" ; "` |
| `has_whatsapp` | `bool | None` | `NULL DEFAULT NULL` | Indicateur externe de présence WhatsApp (`True`, `False` ou `None` si non vérifié) |
| `first_seen_at` | `datetime` | `NOT NULL` | Date et heure UTC de première insertion en base |
| `updated_at` | `datetime` | `NOT NULL` | Date et heure UTC de dernière création ou modification |
| `is_active` | `bool` | `NOT NULL DEFAULT True`, indexé | Indique si le parent figure dans le dernier export importé |

- **Contrainte d'unicité** : `UniqueConstraint("last_name", "first_name", name="uq_parents_last_first_name")`.
- **Relations** :
  - `children: list[ChildRecord]` via `ParentChildLink` (et accès ordonné par `ParentChildLink.position`).
- **Méthodes métier** :
  - `to_domain(ordered_children: list[AttachedChild] | None = None) -> ParentContact` : reconstruit l'entité `ParentContact` du domaine (avec `children`, `units` et `notes_list`) prête pour les exporteurs Excel et vCard.

---

### 1.3 `ChildRecord` (Table `children`)

Enregistrement persistant d'un jeune scout rattaché à un ou plusieurs parents.

| Champ | Type Python / SQLModel | Contraintes SQL | Description |
|-------|------------------------|-----------------|-------------|
| `id` | `int | None` | `PRIMARY KEY AUTOINCREMENT` | Identifiant technique unique |
| `first_name` | `str` | `NOT NULL`, indexé | Prénom normalisé de l'enfant |
| `last_name` | `str` | `NOT NULL`, indexé | Nom de famille normalisé de l'enfant |
| `short_unit` | `str` | `NOT NULL DEFAULT ''`, indexé | Unité scoute courte (ex. `"LOUVETEAUX-JEANNETTES"`, `"FARFADETS"`) |
| `registration_status` | `str` | `NOT NULL DEFAULT ''`, indexé | Statut d'inscription (ex. `"Inscrit(e)"`, `"Pré-inscrit(e)"`) |

- **Contrainte d'unicité** : `UniqueConstraint("last_name", "first_name", name="uq_children_last_first_name")`.
- **Relations** :
  - `parents: list[ParentRecord]` via `ParentChildLink`.
- **Méthodes métier** :
  - `to_domain() -> AttachedChild` : convertit l'enregistrement en `AttachedChild` immuable du domaine.

---

## 2. Objets de Rapport de Différentiel (`sgdf_contacts/persistence/repository.py` / `models.py`)

### 2.1 `FieldChange` (Dataclass immuable)

Représente la modification d'un champ sur une fiche parent lors d'un import.

| Attribut | Type | Description |
|----------|------|-------------|
| `old_value` | `Any` | Valeur du champ avant l'import |
| `new_value` | `Any` | Nouvelle valeur du champ issue de l'import |

### 2.2 `ParentUpdateDiff` (Dataclass immuable)

Représente un parent existant ayant subi au moins une modification lors d'un nouvel import.

| Attribut | Type | Description |
|----------|------|-------------|
| `parent` | `ParentContact` | Fiche consolidée du parent après mise à jour |
| `changes` | `dict[str, FieldChange]` | Dictionnaire des champs modifiés (`member_id`, `primary_mobile_phone`, `children`, `notes`, `is_active`, etc.) |

### 2.3 `ImportDiffReport` (Dataclass)

Rapport complet retourné par chaque synchronisation d'un export d'adhérents en base.

| Attribut | Type | Description |
|----------|------|-------------|
| `created` | `list[ParentContact]` | Nouveaux parents ajoutés en base |
| `updated` | `list[ParentUpdateDiff]` | Parents existants dont les données ou le statut d'activité ont changé |
| `unchanged` | `list[ParentContact]` | Parents actifs présents dans l'export dont aucune donnée n'a changé |
| `deactivated` | `list[ParentContact]` | Parents précédemment actifs absents du nouvel export et passés à `is_active = False` |

---

## 3. Cycle de Vie et Transitions d'État d'un Parent (`ParentRecord`)

1. **Création (`created`)** :
   - Parent absent de la base (ni par `member_id` non vide, ni par `(last_name, first_name)`).
   - Inséré avec `is_active = True`, `has_whatsapp = None`, `first_seen_at = now`, `updated_at = now`.
2. **Inchangé (`unchanged`)** :
   - Parent trouvé en base avec `is_active = True` et toutes ses coordonnées, remarques et enfants (`(first_name, last_name, short_unit, registration_status)`) strictement identiques.
   - Aucune écriture inutile ; `updated_at`, `first_seen_at` et `has_whatsapp` restent intacts.
3. **Mis à jour (`updated`)** :
   - Parent trouvé en base dont au moins un attribut métier, un enfant rattaché ou le statut `is_active` (réactivation depuis `False` vers `True`) a changé.
   - Champs mis à jour, `is_active = True`, `updated_at = now`, `first_seen_at` et `has_whatsapp` préservés.
4. **Désactivé (`deactivated`)** :
   - Parent qui était `is_active = True` avant l'import mais ne figure plus dans le nouvel export.
   - Marqué `is_active = False`, `updated_at = now`, `first_seen_at` et `has_whatsapp` préservés.
