#!/usr/bin/env python3
"""Génération du fichier vCard (`ContactParents.vcf`) pour l'importation dans Google Contacts.

Ce script lit en lecture seule l'onglet `ContactsParents` du classeur Excel
`ContactsParents.xlsx` et génère le fichier `ContactParents.vcf` au format standard
vCard 3.0 (UTF-8) directement importable dans Google Contacts. Chaque fiche contact
contient l'identité du parent (`Prénom Nom`), ses numéros de téléphone (portable
principal, portable secondaire, fixe domicile), son adresse email, son adresse
physique, une note structurée regroupant la liste des enfants avec leurs unités,
le numéro d'adhérent (s'il existe) et d'éventuelles remarques, ainsi que les
étiquettes `"SGDF"` et `"La Rochelle"`.
"""

from __future__ import annotations

from sgdf_contacts.entrypoints.cli_vcf import (
    DEFAULT_CATEGORIES,
    DEFAULT_INPUT_FILE,
    DEFAULT_OUTPUT_FILE,
    PARENT_CONTACTS_HEADERS,
    PARENTS_SHEET_NAME,
    ParentContactCard,
    VcfGenerationError,
    build_parent_note,
    clean_text,
    escape_vcard_value,
    format_children_with_units,
    format_parent_vcard,
    main,
    parse_args,
    read_parent_contacts_excel,
    run_vcf_generation,
    write_vcf_file,
)

__all__ = [
    "DEFAULT_CATEGORIES",
    "DEFAULT_INPUT_FILE",
    "DEFAULT_OUTPUT_FILE",
    "PARENTS_SHEET_NAME",
    "PARENT_CONTACTS_HEADERS",
    "ParentContactCard",
    "VcfGenerationError",
    "build_parent_note",
    "clean_text",
    "escape_vcard_value",
    "format_children_with_units",
    "format_parent_vcard",
    "main",
    "parse_args",
    "read_parent_contacts_excel",
    "run_vcf_generation",
    "write_vcf_file",
]


if __name__ == "__main__":
    raise SystemExit(main())
