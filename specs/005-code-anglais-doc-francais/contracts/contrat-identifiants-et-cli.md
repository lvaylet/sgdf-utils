# Contrat des Identifiants, Interfaces CLI et Sorties Métiers (Phase 1)

## 1. Documentation Principale

- **Fichier à la racine** : `README.md` (remplace `LISEZMOI.md`, qui est supprimé).
- **Langue du contenu** : 100 % en français.

---

## 2. Contrat des Fichiers d'Environnement

### 2.1 `.envrc`

- **Variable d'environnement** : `ENV_TOOL` (valeurs acceptées : `auto`, `flake`, `devbox`).
- **Variable locale** : `selected_tool="${ENV_TOOL:-auto}"`.
- **Fonctions internes** : `activate_flake()`, `activate_devbox()`.
- **Commentaires et messages `echo`** : 100 % en français.

### 2.2 `flake.nix`

- **Identifiants Nix** : `supportedSystems`, `forEachSystem`, `system`, `pythonEnv`, `pythonPackages`.
- **Description, commentaires et `shellHook`** : 100 % en français.

### 2.3 `devbox.json`

- **Scripts définis dans `shell.scripts`** :
  - `check_environment`
  - `test`
  - `check_quality`
- **Messages `shell.init_hook` et sortie de `check_environment`** : 100 % en français.

---

## 3. Contrat des Scripts Python et Interfaces CLI

### 3.1 `extract_parent_contacts.py` (anciennement `extraire_contacts_parents.py`)

- **Invocation CLI** :

  ```bash
  python3 extract_parent_contacts.py [-h] [-i INPUT] [-o OUTPUT]
  ```

- **Options CLI** :
  - `-i`, `--input` : Chemin du fichier d'export SGDF en entrée (défaut : `ExportIndividus.xls`).
  - `-o`, `--output` : Chemin du classeur Excel généré en sortie (défaut : `ContactsParents.xlsx`).
- **Constantes et Symboles Publics** :
  - `DEFAULT_INPUT_FILE = "ExportIndividus.xls"`
  - `DEFAULT_OUTPUT_FILE = "ContactsParents.xlsx"`
  - `SOURCE_SHEET_NAME = "ExportIndividus"`
  - `PARENTS_SHEET_NAME = "ContactsParents"`
  - `PARENT_CONTACTS_HEADERS: tuple[str, ...]` (les 13 en-têtes en français)
  - `ADULT_ROLE_LABELS: dict[tuple[str, str], str]`
  - `ContactExtractionError(Exception)`
  - `AttachedChild`, `AdultGroupProfile`, `ParentContact`
  - `clean_whitespace(value: str) -> str`
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
  - `read_individuals_export_table(input_path: Path) -> tuple[list[str], list[list[str]]]`
  - `build_adult_profiles_index(headers: list[str], rows: list[list[str]]) -> dict[tuple[str, str], AdultGroupProfile]`
  - `extract_and_group_parents(headers: list[str], rows: list[list[str]]) -> list[ParentContact]`
  - `auto_fit_column_widths(worksheet) -> None`
  - `write_parent_contacts_workbook(output_path: Path, source_headers: list[str], source_rows: list[list[str]], parent_contacts: list[ParentContact]) -> None`
  - `run_extraction(input_path: Path, output_path: Path) -> list[ParentContact]`
  - `parse_args(argv: list[str] | None = None) -> argparse.Namespace`
  - `main(argv: list[str] | None = None) -> int`

### 3.2 `generate_contacts_vcf.py` (anciennement `generer_contacts_vcf.py`)

- **Invocation CLI** :

  ```bash
  python3 generate_contacts_vcf.py [-h] [-i INPUT] [-o OUTPUT]
  ```

- **Options CLI** :
  - `-i`, `--input` : Chemin du classeur Excel contenant l'onglet `ContactsParents` en entrée (défaut : `ContactsParents.xlsx`).
  - `-o`, `--output` : Chemin du fichier vCard (`.vcf`) généré en sortie (défaut : `ContactParents.vcf`).
- **Constantes et Symboles Publics** :
  - `DEFAULT_INPUT_FILE = "ContactsParents.xlsx"`
  - `DEFAULT_OUTPUT_FILE = "ContactParents.vcf"`
  - `PARENTS_SHEET_NAME = "ContactsParents"`
  - `DEFAULT_CATEGORIES: tuple[str, ...] = ("SGDF", "La Rochelle")`
  - `PARENT_CONTACTS_HEADERS: tuple[str, ...]` (les 13 en-têtes en français)
  - `VcfGenerationError(Exception)`
  - `ParentContactCard`
  - `clean_text(value: object) -> str`
  - `escape_vcard_value(text: str) -> str`
  - `format_children_with_units(children_names: str, children_units: str) -> str`
  - `build_parent_note(card: ParentContactCard) -> str`
  - `format_parent_vcard(card: ParentContactCard) -> str`
  - `read_parent_contacts_excel(input_path: Path) -> list[ParentContactCard]`
  - `write_vcf_file(output_path: Path, cards: list[ParentContactCard]) -> None`
  - `run_vcf_generation(input_path: Path, output_path: Path) -> list[ParentContactCard]`
  - `parse_args(argv: list[str] | None = None) -> argparse.Namespace`
  - `main(argv: list[str] | None = None) -> int`

---

## 4. Contrat des Fichiers de Tests (`tests/`)

- `tests/test_environment.py` (remplace `tests/test_environnement.py`)
- `tests/test_extract_parent_contacts.py` (remplace `tests/test_extraire_contacts_parents.py`)
- `tests/test_generate_contacts_vcf.py` (remplace `tests/test_generer_contacts_vcf.py`)
- Tous les noms de fonctions `test_*`, fonctions utilitaires, fixtures, constantes et variables locales sont en anglais ; toutes les docstrings et tous les commentaires sont en français.

---

## 5. Contrat Métier Invariant (100 % Préservé)

- Fichiers de données par défaut : `ExportIndividus.xls` → `ContactsParents.xlsx` → `ContactParents.vcf`.
- Onglets de `ContactsParents.xlsx` : `ExportIndividus` et `ContactsParents`.
- 13 colonnes de `ContactsParents` : `Nom`, `Prénom`, `Téléphone portable principal`, `Téléphone portable secondaire`, `Téléphone fixe (domicile)`, `Adresse email`, `Noms des enfants`, `Unités des enfants`, `Rue`, `Code postal`, `Ville`, `Numéro d'adhérent`, `Remarques`.
- 134 parents dédoublonnés et triés par ordre alphabétique français sur l'export de référence.
