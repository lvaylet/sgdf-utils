"""Constantes métier partagées pour l'extraction et l'export des contacts des parents SGDF."""

from __future__ import annotations

DEFAULT_EXPORT_INPUT_FILE = "ExportIndividus.xls"
DEFAULT_PARENTS_WORKBOOK_FILE = "ContactsParents.xlsx"
DEFAULT_VCF_OUTPUT_FILE = "ContactParents.vcf"

SOURCE_SHEET_NAME = "ExportIndividus"
PARENTS_SHEET_NAME = "ContactsParents"

DEFAULT_CATEGORIES: tuple[str, ...] = ("SGDF", "La Rochelle")

PARENT_CONTACTS_HEADERS: tuple[str, ...] = (
    "Nom",
    "Prénom",
    "Téléphone portable principal",
    "Téléphone portable secondaire",
    "Téléphone fixe (domicile)",
    "Adresse email",
    "Noms des enfants",
    "Unités des enfants",
    "Rue",
    "Code postal",
    "Ville",
    "Numéro d'adhérent",
    "Remarques",
)

ADULT_ROLE_LABELS: dict[tuple[str, str], str] = {
    ("271", "M."): "Parent Animateur Farfadet",
    ("271", "Mme"): "Parent Animateur Farfadet",
    ("270", "M."): "Responsable Farfadet",
    ("270", "Mme"): "Responsable Farfadet",
    ("300", "M."): "Responsable de groupe",
    ("300", "Mme"): "Responsable de groupe",
    ("301", "M."): "Responsable de groupe adjoint",
    ("301", "Mme"): "Responsable de groupe adjointe",
    ("307", "M."): "Secrétaire de groupe",
    ("307", "Mme"): "Secrétaire de groupe",
    ("309", "M."): "Trésorier de groupe",
    ("309", "Mme"): "Trésorière de groupe",
    ("316", "M."): "Cléophas de groupe",
    ("316", "Mme"): "Cléophas de groupe",
    ("330", "M."): "Chargé de mission du groupe",
    ("330", "Mme"): "Chargée de mission du groupe",
    ("181", "M."): "Membre du réseau Impeesa",
    ("181", "Mme"): "Membre du réseau Impeesa",
    ("380", "M."): "Coordonnateur du réseau Impeesa local",
    ("380", "Mme"): "Coordonnatrice du réseau Impeesa local",
    ("210", "M."): "Responsable d'unité Louveteaux-Jeannettes",
    ("210", "Mme"): "Responsable d'unité Louveteaux-Jeannettes",
    ("213", "M."): "Chef Louveteaux-Jeannettes",
    ("213", "Mme"): "Cheftaine Louveteaux-Jeannettes",
    ("220", "M."): "Responsable d'unité Scouts-Guides",
    ("220", "Mme"): "Responsable d'unité Scouts-Guides",
    ("223", "M."): "Chef Scouts-Guides",
    ("223", "Mme"): "Cheftaine Scouts-Guides",
    ("230", "M."): "Responsable d'unité Pionniers-Caravelles",
    ("230", "Mme"): "Responsable d'unité Pionniers-Caravelles",
    ("233", "M."): "Chef Pionniers-Caravelles",
    ("233", "Mme"): "Cheftaine Pionniers-Caravelles",
}
