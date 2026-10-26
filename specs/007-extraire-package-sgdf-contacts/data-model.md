# Modèle de Données : Package Modulaire `sgdf_contacts`

**Branche** : `007-extraire-package-sgdf-contacts` | **Date** : 2026-10-26 | **Spécification** : [spec.md](./spec.md)

## 1. Architecture des Entités du Domaine (`sgdf_contacts/domain/models.py`)

### 1.1. `AttachedChild` (dataclass figée `frozen=True`)

Représente un jeune scout rattaché à un parent.

| Champ / Méthode | Type | Description |
| --------------- | ---- | ----------- |
| `first_name` | `str` | Prénom normalisé de l'enfant en casse titre (ex. `Lucas`, `Chloé`) |
| `last_name` | `str` | Nom de famille normalisé de l'enfant en casse titre (ex. `Bernard`) |
| `short_unit` | `str` | Unité scoute courte normalisée (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`) |
| `registration_status` | `str` | Statut d'inscription SGDF (`Inscrit(e)`, `Pré-inscrit(e)`, `Invité(e)`) |
| `format_full_name()` | `() -> str` | Retourne le nom complet sous la forme `Prénom Nom` |

### 1.2. `AdultGroupProfile` (dataclass)

Représente l'inscription adulte d'un membre du groupe SGDF permettant d'enrichir la fiche d'un parent.

| Champ | Type | Défaut | Description |
| ----- | ---- | ------ | ----------- |
| `last_name` | `str` | *(requis)* | Nom de famille normalisé en casse titre |
| `first_name` | `str` | *(requis)* | Prénom normalisé en casse titre |
| `member_id` | `str` | `""` | Code adhérent SGDF (`Individu.CodeAdherent`) |
| `roles_and_delegations` | `list[str]` | `[]` | Liste dédoublonnée des rôles adultes et délégations en français |
| `mobile_phone_1` | `str` | `""` | Téléphone portable 1 normalisé |
| `mobile_phone_2` | `str` | `""` | Téléphone portable 2 normalisé |
| `home_phone` | `str` | `""` | Téléphone fixe domicile normalisé |
| `email` | `str` | `""` | Courriel personnel ou dédié SGDF |
| `street` | `str` | `""` | Lignes de rue jointes et normalisées en casse titre |
| `postal_code` | `str` | `""` | Code postal normalisé |
| `city` | `str` | `""` | Ville normalisée en casse titre |

### 1.3. `ParentContact` (dataclass)

Représente la fiche consolidée et dédoublonnée d'un parent de jeune(s) scout(s).

| Champ / Propriété / Méthode | Type | Description |
| --------------------------- | ---- | ----------- |
| `last_name` | `str` | Nom de famille normalisé en casse titre |
| `first_name` | `str` | Prénom normalisé en casse titre |
| `primary_mobile_phone` | `str` | Téléphone portable principal au format international (`+336...` / `+337...`) |
| `secondary_mobile_phone` | `str` | Téléphone portable secondaire au format international |
| `landline_phone` | `str` | Téléphone fixe domicile au format international |
| `email_address` | `str` | Adresse courriel du parent |
| `children` | `list[AttachedChild]` | Enfants rattachés sans doublon |
| `units` | `list[str]` | Unités courtes distinctes des enfants |
| `street` | `str` | Rue normalisée en casse titre |
| `postal_code` | `str` | Code postal |
| `city` | `str` | Ville normalisée en casse titre |
| `member_id` | `str` | Numéro d'adhérent SGDF du parent |
| `notes_list` | `list[str]` | Liste ordonnée et dédoublonnée des remarques |
| `waha_chat_id` *(propriété)* | `str` | Identifiant WhatsApp WAHA dérivé de `primary_mobile_phone` (`+33687966975` → `33687966975@c.us`, ou `""` si vide) |
| `children_names` *(propriété)* | `str` | Noms complets des enfants séparés par `, ` |
| `children_units` *(propriété)* | `str` | Unités courtes des enfants dans le même ordre, séparées par `, ` |
| `notes` *(propriété)* | `str` | Remarques consolidées séparées par ` ; ` |
| `add_child(child)` | `(AttachedChild) -> None` | Ajoute un enfant, son unité et sa remarque éventuelle de statut |
| `add_note(note)` | `(str) -> None` | Ajoute une remarque nettoyée sans doublon |
| `merge_contact_info(...)` | `(...) -> None` | Fusionne les coordonnées sans écraser les valeurs déjà présentes et réorganise les téléphones |
| `reorganize_phones()` | `() -> None` | Promeut un portable valide (`+336`/`+337`) vers `primary_mobile_phone` si celui-ci est vide |
| `to_excel_row()` | `() -> list[str]` | Convertit la fiche en liste des 13 colonnes Excel attendues |
| `to_contact_card(categories)` | `(...) -> ParentContactCard` | Convertit directement la fiche `ParentContact` en `ParentContactCard` pour l'export vCard |

### 1.4. `ParentContactCard` (dataclass figée `frozen=True`)

Représente la fiche d'un parent prête à être sérialisée au format vCard 3.0 (construite soit depuis `ParentContact.to_contact_card()`, soit depuis la lecture de `ContactsParents.xlsx`).

| Champ / Propriété | Type | Défaut | Description |
| ----------------- | ---- | ------ | ----------- |
| `last_name` | `str` | *(requis)* | Nom de famille du parent |
| `first_name` | `str` | *(requis)* | Prénom du parent |
| `primary_mobile_phone` | `str` | `""` | Téléphone portable principal |
| `secondary_mobile_phone` | `str` | `""` | Téléphone portable secondaire |
| `landline_phone` | `str` | `""` | Téléphone fixe domicile |
| `email_address` | `str` | `""` | Adresse email |
| `children_names` | `str` | `""` | Liste des enfants séparés par `, ` |
| `children_units` | `str` | `""` | Liste des unités séparées par `, ` |
| `street` | `str` | `""` | Rue |
| `postal_code` | `str` | `""` | Code postal |
| `city` | `str` | `""` | Ville |
| `member_id` | `str` | `""` | Numéro d'adhérent |
| `notes` | `str` | `""` | Remarques consolidées |
| `categories` | `tuple[str, ...]` | `DEFAULT_CATEGORIES` | Étiquettes vCard (`("SGDF", "La Rochelle")`) |
| `formatted_full_name` *(propriété)* | `str` | — | Nom complet sous la forme `Prénom Nom` |

## 2. Constantes Partagées (`sgdf_contacts/domain/constants.py`)

- `PARENT_CONTACTS_HEADERS`: tuple des 13 intitulés de colonnes en français de l'onglet `ContactsParents`.
- `ADULT_ROLE_LABELS`: dictionnaire `(code_fonction, civilite) -> libellé_français`.
- `DEFAULT_CATEGORIES`: `("SGDF", "La Rochelle")`.
- `SOURCE_SHEET_NAME`: `"ExportIndividus"`.
- `PARENTS_SHEET_NAME`: `"ContactsParents"`.
- `DEFAULT_EXPORT_INPUT_FILE`: `"ExportIndividus.xls"`.
- `DEFAULT_PARENTS_WORKBOOK_FILE`: `"ContactsParents.xlsx"`.
- `DEFAULT_VCF_OUTPUT_FILE`: `"ContactParents.vcf"`.
