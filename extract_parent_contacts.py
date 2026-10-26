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

import argparse
import sys
from pathlib import Path

from sgdf_contacts.domain import (
    ADULT_ROLE_LABELS,
    PARENT_CONTACTS_HEADERS,
    PARENTS_SHEET_NAME,
    SOURCE_SHEET_NAME,
    AdultGroupProfile,
    AttachedChild,
    ContactExtractionError,
    ParentContact,
    clean_whitespace,
    extract_delegation_roles,
    is_valid_mobile_phone,
    join_street_lines,
    normalize_address_part,
    normalize_adult_role,
    normalize_first_name,
    normalize_last_name,
    normalize_phone,
    normalize_short_unit,
    parent_sort_key,
    strip_accents,
)
from sgdf_contacts.domain import (
    DEFAULT_EXPORT_INPUT_FILE as DEFAULT_INPUT_FILE,
)
from sgdf_contacts.domain import (
    DEFAULT_PARENTS_WORKBOOK_FILE as DEFAULT_OUTPUT_FILE,
)
from sgdf_contacts.exporters import (
    auto_fit_column_widths,
    write_parent_contacts_workbook,
)
from sgdf_contacts.parsers import (
    build_adult_profiles_index,
    extract_and_group_parents,
    read_individuals_export_table,
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


def run_extraction(input_path: Path, output_path: Path) -> list[ParentContact]:
    """Exécute la chaîne complète : lecture seule, extraction, dédoublonnage, tri et écriture Excel."""
    headers, rows = read_individuals_export_table(input_path)
    parent_contacts = extract_and_group_parents(headers, rows)
    write_parent_contacts_workbook(
        output_path=output_path,
        source_headers=headers,
        source_rows=rows,
        parent_contacts=parent_contacts,
    )
    return parent_contacts


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Analyse les arguments en ligne de commande (descriptions d'aide en français)."""
    parser = argparse.ArgumentParser(
        prog="extract_parent_contacts.py",
        description=(
            "Extrait, dédoublonne et trie les contacts des parents des jeunes scouts SGDF "
            "depuis l'export intranet vers l'onglet 'ContactsParents'."
        ),
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path(DEFAULT_INPUT_FILE),
        help=f"Chemin du fichier d'export SGDF en entrée (défaut : {DEFAULT_INPUT_FILE}).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(DEFAULT_OUTPUT_FILE),
        help=f"Chemin du classeur Excel généré en sortie (défaut : {DEFAULT_OUTPUT_FILE}).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Point d'entrée principal du script en ligne de commande."""
    args = parse_args(argv)
    try:
        contacts = run_extraction(
            input_path=args.input,
            output_path=args.output,
        )
    except ContactExtractionError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    print(
        f"Extraction terminée avec succès : {len(contacts)} parents uniques enregistrés "
        f"dans l'onglet '{PARENTS_SHEET_NAME}' du fichier '{args.output}'."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
