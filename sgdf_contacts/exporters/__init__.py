"""Sous-package des générateurs de sortie (`ContactsParents.xlsx` et `ContactParents.vcf`)."""

from __future__ import annotations

from sgdf_contacts.exporters.excel import (
    auto_fit_column_widths,
    write_parent_contacts_workbook,
)
from sgdf_contacts.exporters.vcard import (
    build_parent_note,
    escape_vcard_value,
    format_children_with_units,
    format_parent_vcard,
    format_vcf_content,
    to_contact_card,
    write_vcf_file,
)

__all__ = [
    "auto_fit_column_widths",
    "build_parent_note",
    "escape_vcard_value",
    "format_children_with_units",
    "format_parent_vcard",
    "format_vcf_content",
    "to_contact_card",
    "write_parent_contacts_workbook",
    "write_vcf_file",
]
