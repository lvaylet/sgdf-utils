"""Point d'entrée CLI (`sgdf-vcf`) de génération du fichier vCard (`ContactParents.vcf`)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sgdf_contacts.domain import (
    DEFAULT_CATEGORIES,
    PARENT_CONTACTS_HEADERS,
    PARENTS_SHEET_NAME,
    ParentContactCard,
    VcfGenerationError,
    clean_text,
)
from sgdf_contacts.domain import (
    DEFAULT_PARENTS_WORKBOOK_FILE as DEFAULT_INPUT_FILE,
)
from sgdf_contacts.domain import (
    DEFAULT_VCF_OUTPUT_FILE as DEFAULT_OUTPUT_FILE,
)
from sgdf_contacts.exporters import (
    build_parent_note,
    escape_vcard_value,
    format_children_with_units,
    format_parent_vcard,
    write_vcf_file,
)
from sgdf_contacts.parsers import read_parent_contacts_excel

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


def run_vcf_generation(
    input_path: Path,
    output_path: Path,
) -> list[ParentContactCard]:
    """Exécute la chaîne complète : lecture seule de `ContactsParents.xlsx` et génération `.vcf`."""
    cards = read_parent_contacts_excel(input_path)
    write_vcf_file(output_path=output_path, cards=cards)
    return cards


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Analyse les arguments en ligne de commande (descriptions d'aide en français)."""
    parser = argparse.ArgumentParser(
        prog="sgdf-vcf",
        description=(
            "Génère le fichier 'ContactParents.vcf' importable dans Google Contacts "
            "à partir de l'onglet 'ContactsParents' de 'ContactsParents.xlsx'."
        ),
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path(DEFAULT_INPUT_FILE),
        help=(
            "Chemin du classeur Excel contenant l'onglet 'ContactsParents' en entrée "
            f"(défaut : {DEFAULT_INPUT_FILE})."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(DEFAULT_OUTPUT_FILE),
        help=(
            "Chemin du fichier vCard (.vcf) généré en sortie "
            f"(défaut : {DEFAULT_OUTPUT_FILE})."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Point d'entrée principal de la commande `sgdf-vcf` / `generate_contacts_vcf.py`."""
    args = parse_args(argv)
    try:
        cards = run_vcf_generation(
            input_path=args.input,
            output_path=args.output,
        )
    except VcfGenerationError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    print(
        f"Génération terminée avec succès : {len(cards)} contacts parents écrits "
        f"dans le fichier '{args.output}'."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
