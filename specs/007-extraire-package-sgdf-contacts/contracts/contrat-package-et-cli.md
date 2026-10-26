# Contrat d'Interface : Package `sgdf_contacts` et Rétrocompatibilité CLI

**Branche** : `007-extraire-package-sgdf-contacts` | **Date** : 2026-10-26 | **Spécification** : [spec.md](../spec.md)

## 1. Contrat de l'API Publique du Package `sgdf_contacts`

### 1.1. `sgdf_contacts.domain`

Expose sans aucune dépendance externe (bibliothèque standard Python uniquement) :

- **Entités** :
  - `AttachedChild(first_name: str, last_name: str, short_unit: str, registration_status: str)`
  - `AdultGroupProfile(...)`
  - `ParentContact(...)` avec :
    - `contact.waha_chat_id -> str` (`"+33687966975"` → `"33687966975@c.us"`, `""` → `""`)
    - `contact.to_excel_row() -> list[str]`
    - `contact.to_contact_card(categories: tuple[str, ...] = DEFAULT_CATEGORIES) -> ParentContactCard`
  - `ParentContactCard(...)`
- **Exceptions** :
  - `ContactExtractionError(Exception)`
  - `VcfGenerationError(Exception)`
- **Constantes** :
  - `PARENT_CONTACTS_HEADERS: tuple[str, ...]`
  - `ADULT_ROLE_LABELS: dict[tuple[str, str], str]`
  - `DEFAULT_CATEGORIES: tuple[str, ...]`
  - `SOURCE_SHEET_NAME: str` (`"ExportIndividus"`)
  - `PARENTS_SHEET_NAME: str` (`"ContactsParents"`)
- **Fonctions pures de normalisation et de tri** :
  - `clean_whitespace(value: str) -> str`
  - `clean_text(value: object) -> str`
  - `normalize_last_name(raw_last_name: str) -> str`
  - `normalize_first_name(raw_first_name: str) -> str`
  - `normalize_phone(raw_phone: str) -> str`
  - `is_valid_mobile_phone(phone: str) -> bool`
  - `strip_accents(text: str) -> str`
  - `parent_sort_key(contact: ParentContact) -> tuple[str, str, str, str]`
  - `normalize_short_unit(structure_name: str, role_code: str = "") -> str`
  - `normalize_adult_role(title: str, role_code: str, male_label: str, female_label: str) -> str`
  - `extract_delegation_roles(delegations_text: str, title: str = "M.") -> list[str]`
  - `normalize_address_part(raw_text: str) -> str`
  - `join_street_lines(line1: str, line2: str = "", line3: str = "") -> str`

### 1.2. `sgdf_contacts.parsers`

- `read_individuals_export_table(input_source: Path | bytes | BinaryIO) -> tuple[list[str], list[list[str]]]` :
  - Accepte un `Path` sur disque, un objet `bytes` ou un flux binaire (`io.BytesIO`).
  - Lève `ContactExtractionError` avec un message explicite en français si le fichier est introuvable, illisible ou si le tableau HTML / l'en-tête `Individu.Nom` est absent.
- `build_adult_profiles_index(headers: list[str], rows: list[list[str]]) -> dict[tuple[str, str], AdultGroupProfile]`
- `extract_and_group_parents(headers: list[str], rows: list[list[str]]) -> list[ParentContact]`
- `read_parent_contacts_excel(input_path: Path) -> list[ParentContactCard]`

### 1.3. `sgdf_contacts.exporters`

- `write_parent_contacts_workbook(output_path: Path | BinaryIO, source_headers: list[str], source_rows: list[list[str]], parent_contacts: list[ParentContact]) -> bytes` :
  - Écrit le classeur `.xlsx` à deux onglets (`ExportIndividus` et `ContactsParents`) vers un `Path` sur disque ou vers un flux `io.BytesIO` en mémoire, et retourne les octets générés.
- `format_parent_vcard(contact_or_card: ParentContact | ParentContactCard) -> str` :
  - Sérialise un `ParentContact` ou une `ParentContactCard` en bloc `VCARD` 3.0 (séparateur `\r\n`).
- `format_vcf_content(contacts: Sequence[ParentContact | ParentContactCard]) -> str` :
  - Sérialise une liste de `ParentContact` ou de `ParentContactCard` en chaîne `.vcf` complète terminée par `\r\n`.
- `write_vcf_file(output_path: Path, cards: Sequence[ParentContact | ParentContactCard]) -> None` :
  - Écrit directement sur disque un fichier `.vcf` UTF-8 à partir d'une séquence de `ParentContact` ou de `ParentContactCard`.

## 2. Contrat de Rétrocompatibilité CLI et Symboles Ré-exportés

1. **`extract_parent_contacts.py`** :
   - CLI : `python3 extract_parent_contacts.py [-i/--input ExportIndividus.xls] [-o/--output ContactsParents.xlsx] [-h/--help]`
   - Symboles publics ré-exportés pour la rétrocompatibilité des tests : `PARENT_CONTACTS_HEADERS`, `PARENTS_SHEET_NAME`, `SOURCE_SHEET_NAME`, `ADULT_ROLE_LABELS`, `AttachedChild`, `AdultGroupProfile`, `ParentContact`, `ContactExtractionError`, `read_individuals_export_table`, `build_adult_profiles_index`, `extract_and_group_parents`, `write_parent_contacts_workbook`, `run_extraction`, `parse_args`, `main` ainsi que les fonctions de normalisation.
2. **`generate_contacts_vcf.py`** :
   - CLI : `python3 generate_contacts_vcf.py [-i/--input ContactsParents.xlsx] [-o/--output ContactParents.vcf] [-h/--help]`
   - Symboles publics ré-exportés pour la rétrocompatibilité des tests : `PARENT_CONTACTS_HEADERS`, `PARENTS_SHEET_NAME`, `DEFAULT_CATEGORIES`, `ParentContactCard`, `VcfGenerationError`, `escape_vcard_value`, `format_children_with_units`, `build_parent_note`, `format_parent_vcard`, `read_parent_contacts_excel`, `write_vcf_file`, `run_vcf_generation`, `parse_args`, `main`.
