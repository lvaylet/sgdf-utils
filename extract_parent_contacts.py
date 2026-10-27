#!/usr/bin/env python3
"""Extraction et regroupement des contacts des parents des jeunes scouts SGDF.

Ce script lit en lecture seule le fichier d'export SGDF (`ExportIndividus.xls`),
extrait l'ensemble des représentants légaux (`1`, `2`, `3`) des jeunes du groupe,
les dédoublonne sur le couple `(Nom, Prénom)` afin de regrouper les fratries et
leurs unités courtes, enrichit les fiches avec les numéros d'adhérent et les rôles
adultes éventuels (ex. Parent Animateur Farfadet), trie les entrées par ordre
alphabétique français sur `(Nom, Prénom)` et génère le classeur Excel
`ContactsParents.xlsx` contenant les onglets `ExportIndividus` et `ContactsParents`.
"""

from __future__ import annotations

from sgdf_contacts.entrypoints.cli_extract import (
    ADULT_ROLE_LABELS,
    DEFAULT_INPUT_FILE,
    DEFAULT_OUTPUT_FILE,
    PARENT_CONTACTS_HEADERS,
    PARENTS_SHEET_NAME,
    SOURCE_SHEET_NAME,
    AdultGroupProfile,
    AttachedChild,
    ContactExtractionError,
    ParentContact,
    auto_fit_column_widths,
    build_adult_profiles_index,
    clean_whitespace,
    extract_and_group_parents,
    extract_delegation_roles,
    is_valid_mobile_phone,
    join_street_lines,
    main,
    normalize_address_part,
    normalize_adult_role,
    normalize_first_name,
    normalize_last_name,
    normalize_phone,
    normalize_short_unit,
    parent_sort_key,
    parse_args,
    read_individuals_export_table,
    run_extraction,
    strip_accents,
    write_parent_contacts_workbook,
)

__all__ = [
    "ADULT_ROLE_LABELS",
    "DEFAULT_INPUT_FILE",
    "DEFAULT_OUTPUT_FILE",
    "PARENTS_SHEET_NAME",
    "PARENT_CONTACTS_HEADERS",
    "SOURCE_SHEET_NAME",
    "AdultGroupProfile",
    "AttachedChild",
    "ContactExtractionError",
    "ParentContact",
    "auto_fit_column_widths",
    "build_adult_profiles_index",
    "clean_whitespace",
    "extract_and_group_parents",
    "extract_delegation_roles",
    "is_valid_mobile_phone",
    "join_street_lines",
    "main",
    "normalize_address_part",
    "normalize_adult_role",
    "normalize_first_name",
    "normalize_last_name",
    "normalize_phone",
    "normalize_short_unit",
    "parent_sort_key",
    "parse_args",
    "read_individuals_export_table",
    "run_extraction",
    "strip_accents",
    "write_parent_contacts_workbook",
]


if __name__ == "__main__":
    raise SystemExit(main())
