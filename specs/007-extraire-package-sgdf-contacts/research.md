# Recherche Technique : Extraction du Cœur Métier dans un Package Modulaire `sgdf_contacts`

**Branche** : `007-extraire-package-sgdf-contacts` | **Date** : 2026-10-26 | **Spécification** : [spec.md](./spec.md)

## 1. Découpage interne du package `sgdf_contacts/`

- **Decision** :
  - Organiser `sgdf_contacts/` en trois sous-packages explicites conformément à l'issue #3 :
    1. `sgdf_contacts/domain/` :
       - `constants.py` : `PARENT_CONTACTS_HEADERS`, `ADULT_ROLE_LABELS`, `DEFAULT_CATEGORIES`, `SOURCE_SHEET_NAME`, `PARENTS_SHEET_NAME`, `DEFAULT_EXPORT_INPUT_FILE`, `DEFAULT_PARENTS_WORKBOOK_FILE`, `DEFAULT_VCF_OUTPUT_FILE`.
       - `exceptions.py` : `ContactExtractionError`, `VcfGenerationError`.
       - `normalization.py` : `clean_whitespace`, `clean_text`, `normalize_last_name`, `normalize_first_name`, `normalize_phone`, `is_valid_mobile_phone`, `strip_accents`, `parent_sort_key`, `normalize_short_unit`, `normalize_adult_role`, `extract_delegation_roles`, `normalize_address_part`, `join_street_lines`.
       - `models.py` : `AttachedChild`, `AdultGroupProfile`, `ParentContact` (avec `waha_chat_id` et `to_contact_card()`), `ParentContactCard`.
    2. `sgdf_contacts/parsers/` :
       - `individuals_xls.py` : `read_individuals_export_table`, `build_adult_profiles_index`, `extract_and_group_parents`.
       - `parents_excel.py` : `read_parent_contacts_excel`.
    3. `sgdf_contacts/exporters/` :
       - `excel.py` : `auto_fit_column_widths`, `write_parent_contacts_workbook`.
       - `vcard.py` : `escape_vcard_value`, `format_children_with_units`, `build_parent_note`, `to_contact_card`, `format_parent_vcard`, `format_vcf_content`, `write_vcf_file`.
- **Rationale** :
  - Respecte strictement l'architecture hexagonale (Ports & Adapters) décrite dans les issues #2 et #3 : `domain` ne dépend que de la bibliothèque standard Python (0 dépendance tierce), tandis que `parsers` et `exporters` isolent les dépendances à `beautifulsoup4`/`lxml` et `openpyxl`.
  - Élimine toute duplication de `PARENT_CONTACTS_HEADERS`, des constantes de noms d'onglets et des fonctions de nettoyage de texte entre les deux scripts.
- **Alternatives considered** :
  - *Mettre tout `domain` dans un seul fichier `domain.py`* : Écarté au profit d'un sous-package `sgdf_contacts/domain/` car l'issue #3 mentionne explicitement l'arborescence `sgdf_contacts/domain/`, `sgdf_contacts/parsers/`, `sgdf_contacts/exporters/`, et réexporter tout dans `sgdf_contacts/domain/__init__.py` offre à la fois la lisibilité de petits fichiers spécialisés et la simplicité d'importation (`from sgdf_contacts.domain import ...`).

## 2. Support de `Path` et `bytes` en mémoire dans `read_individuals_export_table`

- **Decision** :
  - Typer le paramètre d'entrée de `read_individuals_export_table(source: Path | bytes | BinaryIO) -> tuple[list[str], list[list[str]]]` :
    - Si `isinstance(source, (bytes, bytearray))` : utiliser directement ces octets (et définir le libellé de source pour les messages d'erreur comme `"<flux en mémoire>"`).
    - Si `hasattr(source, "read")` (ex. `io.BytesIO`) : lire les octets via `source.read()`.
    - Sinon (chemin `Path` ou `str` converti en `Path`) : vérifier `input_path.is_file()` et lire `input_path.read_bytes()` en levant `ContactExtractionError` en cas de fichier absent ou illisible.
- **Rationale** :
  - Répond à l'exigence de l'issue #3 (« supportant à la fois un `Path` et un flux `bytes` en mémoire (préparation à l'upload HTTP) ») tout en conservant les messages d'erreur exacts en français attendus lorsque `source` est un `Path`.
- **Alternatives considered** :
  - *Créer deux fonctions distinctes `read_individuals_export_file` et `read_individuals_export_bytes`* : Moins ergonomique que le support polymorphe direct sur `read_individuals_export_table`, qui est explicitement demandé dans l'issue #3.

## 3. Support de `Path` et `io.BytesIO` dans `write_parent_contacts_workbook`

- **Decision** :
  - Permettre à `write_parent_contacts_workbook(output_target: Path | BinaryIO | None = None, *, source_headers: list[str], source_rows: list[list[str]], parent_contacts: list[ParentContact], output_path: Path | None = None) -> bytes` d'accepter :
    - Un `Path` (ou l'argument nommé historique `output_path: Path`) : crée le dossier parent `output_path.parent.mkdir(parents=True, exist_ok=True)` et sauvegarde le classeur sur disque.
    - Un flux binaire en mémoire (`io.BytesIO` / objet doté de `.write()`) : sauvegarde le classeur dans ce flux et remet le curseur au début (`seek(0)` si supporté).
    - Retourne également les octets générés ou écrit directement dans la cible fournie.
- **Rationale** :
  - Garantit 100 % de compatibilité avec les appels existants `write_parent_contacts_workbook(output_path=..., source_headers=..., source_rows=..., parent_contacts=...)` et `write_parent_contacts_workbook(path, headers, rows, contacts)` tout en permettant d'écrire dans un `io.BytesIO` en mémoire sans toucher au disque.
- **Alternatives considered** :
  - *Imposer uniquement `Path` dans `write_parent_contacts_workbook`* : Ne répondrait pas à l'exigence de l'issue #3 (« `write_parent_contacts_workbook` + support d'écriture en mémoire `io.BytesIO` »).

## 4. Génération vCard 3.0 directe depuis `list[ParentContact]` et `list[ParentContactCard]`

- **Decision** :
  - Ajouter sur `ParentContact` une méthode `to_contact_card(categories: tuple[str, ...] = DEFAULT_CATEGORIES) -> ParentContactCard` qui construit directement une `ParentContactCard` à partir des attributs et propriétés de `ParentContact` (`children_names`, `children_units`, `notes`, etc.).
  - Accepter indifféremment `ParentContact | ParentContactCard` dans `format_parent_vcard`, `build_parent_note`, `format_vcf_content` et `write_vcf_file` (`Sequence[ParentContact | ParentContactCard]`).
- **Rationale** :
  - Permet de générer un fichier `.vcf` ou une chaîne vCard directement depuis `list[ParentContact]` en mémoire sans passer par un fichier `.xlsx` intermédiaire, tout en conservant `ParentContactCard` pour la lecture depuis `ContactsParents.xlsx`.
  - Garantit par construction que le bloc vCard généré depuis un `ParentContact` est bit-à-bit identique à celui généré après passage par `ContactsParents.xlsx`.
- **Alternatives considered** :
  - *Dupliquer la logique de formatage vCard pour `ParentContact` et `ParentContactCard`* : Contraire au principe de non-duplication et au principe YAGNI.

## 5. Propriété `waha_chat_id` sur `ParentContact`

- **Decision** :
  - Implémenter sur `ParentContact` la propriété :
    ```python
    @property
    def waha_chat_id(self) -> str:
        """Retourne l'identifiant de conversation WhatsApp (WAHA) dérivé du portable principal."""
        phone = self.primary_mobile_phone.strip()
        if not phone:
            return ""
        digits = phone.lstrip("+")
        return f"{digits}@c.us" if digits else ""
    ```
- **Rationale** :
  - Convertit `+33687966975` en `33687966975@c.us` comme demandé dans l'issue #3 et retourne `""` si aucun numéro portable principal n'est renseigné.
- **Alternatives considered** :
  - *Aucune*.
