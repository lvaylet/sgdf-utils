"""Sous-package du domaine métier pur (sans dépendance externe) pour `sgdf_contacts`."""

from __future__ import annotations

from sgdf_contacts.domain.constants import (
    ADULT_ROLE_LABELS,
    DEFAULT_CATEGORIES,
    DEFAULT_EXPORT_INPUT_FILE,
    DEFAULT_PARENTS_WORKBOOK_FILE,
    DEFAULT_VCF_OUTPUT_FILE,
    PARENT_CONTACTS_HEADERS,
    PARENTS_SHEET_NAME,
    SOURCE_SHEET_NAME,
)
from sgdf_contacts.domain.exceptions import ContactExtractionError, VcfGenerationError
from sgdf_contacts.domain.models import (
    AdultGroupProfile,
    AttachedChild,
    ParentContact,
    ParentContactCard,
)
from sgdf_contacts.domain.normalization import (
    clean_text,
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

__all__ = [
    "ADULT_ROLE_LABELS",
    "DEFAULT_CATEGORIES",
    "DEFAULT_EXPORT_INPUT_FILE",
    "DEFAULT_PARENTS_WORKBOOK_FILE",
    "DEFAULT_VCF_OUTPUT_FILE",
    "PARENTS_SHEET_NAME",
    "PARENT_CONTACTS_HEADERS",
    "SOURCE_SHEET_NAME",
    "AdultGroupProfile",
    "AttachedChild",
    "ContactExtractionError",
    "ParentContact",
    "ParentContactCard",
    "VcfGenerationError",
    "clean_text",
    "clean_whitespace",
    "extract_delegation_roles",
    "is_valid_mobile_phone",
    "join_street_lines",
    "normalize_address_part",
    "normalize_adult_role",
    "normalize_first_name",
    "normalize_last_name",
    "normalize_phone",
    "normalize_short_unit",
    "parent_sort_key",
    "strip_accents",
]
