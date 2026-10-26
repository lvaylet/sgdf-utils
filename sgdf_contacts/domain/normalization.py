"""Fonctions pures de nettoyage, de normalisation et de tri pour le domaine SGDF."""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING

from sgdf_contacts.domain.constants import ADULT_ROLE_LABELS

if TYPE_CHECKING:
    from sgdf_contacts.domain.models import ParentContact


def clean_whitespace(value: str) -> str:
    """Supprime les espaces superflus en début, fin et milieu de chaîne."""
    return re.sub(r"\s+", " ", value.strip())


def clean_text(value: object) -> str:
    """Convertit une valeur de cellule Excel en chaîne nettoyée de ses espaces superflus."""
    if value is None:
        return ""
    return clean_whitespace(str(value))


def normalize_last_name(raw_last_name: str) -> str:
    """Normalise un nom de famille avec la première lettre de chaque partie en majuscule et le reste en minuscules."""
    text = clean_whitespace(raw_last_name).lower()
    if not text:
        return ""
    return re.sub(
        r"(^|[\s\-'])([^\s\-'])",
        lambda match: match.group(1) + match.group(2).upper(),
        text,
    )


def normalize_first_name(raw_first_name: str) -> str:
    """Normalise un prénom avec la première lettre de chaque partie en majuscule et le reste en minuscules."""
    text = clean_whitespace(raw_first_name).lower()
    if not text:
        return ""
    return re.sub(
        r"(^|[\s\-'])([^\s\-'])",
        lambda match: match.group(1) + match.group(2).upper(),
        text,
    )


def normalize_phone(raw_phone: str) -> str:
    """Normalise un numéro de téléphone au format international compact sans espaces (ex. +33687966975)."""
    text = raw_phone.strip()
    if not text:
        return ""

    # Supprimer l'indication facultative (0) parfois présente après l'indicatif (+33(0)6...)
    text = re.sub(r"\(\s*0\s*\)", "", text)

    has_plus_prefix = text.startswith("+")
    digits = re.sub(r"\D", "", text)
    if not digits:
        return ""

    if has_plus_prefix:
        normalized_phone = f"+{digits}"
    elif digits.startswith("00") and len(digits) > 2:
        normalized_phone = f"+{digits[2:]}"
    elif digits.startswith("0") and len(digits) > 1:
        normalized_phone = f"+33{digits[1:]}"
    elif len(digits) == 9 and digits[0] in "123456789":
        normalized_phone = f"+33{digits}"
    elif digits.startswith("33") and len(digits) == 11:
        normalized_phone = f"+{digits}"
    else:
        normalized_phone = f"+{digits}"

    # Corriger le cas +3306... (13 caractères avec un 0 superflu après +33)
    if normalized_phone.startswith("+330") and len(normalized_phone) == 13:
        normalized_phone = f"+33{normalized_phone[4:]}"

    return normalized_phone


def is_valid_mobile_phone(phone: str) -> bool:
    """Indique si le numéro normalisé est un téléphone portable français valide (+336 ou +337)."""
    return phone.startswith(("+336", "+337"))


def strip_accents(text: str) -> str:
    """Retourne une chaîne dépourvue de marques diacritiques pour le tri alphabétique français."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def parent_sort_key(contact: ParentContact) -> tuple[str, str, str, str]:
    """Clé de tri alphabétique français sur le Nom puis sur le Prénom."""
    return (
        strip_accents(contact.last_name).upper(),
        contact.last_name,
        strip_accents(contact.first_name).lower(),
        contact.first_name,
    )


def normalize_short_unit(structure_name: str, role_code: str = "") -> str:
    """Convertit un nom de structure ou code fonction SGDF en nom d'unité court normalisé."""
    code = clean_whitespace(role_code)
    upper_structure = strip_accents(clean_whitespace(structure_name)).upper()

    if code in ("170", "270", "271") or "FARFADET" in upper_structure:
        return "Farfadets"
    if (
        code in ("110", "210", "213")
        or "LOUVETEAU" in upper_structure
        or "JEANNETTE" in upper_structure
    ):
        return "Louveteaux-Jeannettes"
    if (
        code in ("120", "220", "223")
        or "SCOUTS GUIDES" in upper_structure
        or "SCOUT" in upper_structure
    ):
        return "Scouts-Guides"
    if (
        code in ("130", "230", "233")
        or "PIONNIER" in upper_structure
        or "CARAVELLE" in upper_structure
    ):
        return "Pionniers-Caravelles"
    if code in ("140", "240", "243") or "COMPAGNON" in upper_structure:
        return "Compagnons"
    return clean_whitespace(structure_name)


def normalize_adult_role(
    title: str,
    role_code: str,
    male_label: str,
    female_label: str,
) -> str:
    """Retourne le libellé lisible en français du rôle adulte au sein du groupe SGDF."""
    code = clean_whitespace(role_code)
    normalized_title = clean_whitespace(title)
    key = (code, "Mme" if normalized_title == "Mme" else "M.")
    if key in ADULT_ROLE_LABELS:
        return ADULT_ROLE_LABELS[key]

    raw_label = (
        female_label
        if (normalized_title == "Mme" and female_label.strip())
        else male_label
    )
    text = clean_whitespace(raw_label)
    if not text:
        return ""
    return text[0].upper() + text[1:].lower()


def extract_delegation_roles(delegations_text: str, title: str = "M.") -> list[str]:
    """Extrait les rôles adultes mentionnés dans la colonne `Inscription.Delegations`."""
    text = clean_whitespace(delegations_text)
    if not text:
        return []

    roles: list[str] = []
    for segment in text.split(";"):
        chunk = segment.strip()
        if not chunk:
            continue
        match = re.match(r"^(\d+)\s*-\s*([^(]+)", chunk)
        if match:
            delegation_code = match.group(1).strip()
            raw_label = match.group(2).strip()
            role = normalize_adult_role(title, delegation_code, raw_label, raw_label)
            if role and role not in roles:
                roles.append(role)
        else:
            roles.append(chunk)
    return roles


def normalize_address_part(raw_text: str) -> str:
    """Normalise une composante d'adresse en minuscules avec la première lettre de chaque mot en majuscule."""
    text = clean_whitespace(raw_text).lower()
    if not text:
        return ""
    return re.sub(
        r"(^|[\s\-'/,])([^\s\-'/,])",
        lambda match: match.group(1) + match.group(2).upper(),
        text,
    )


def join_street_lines(
    line1: str,
    line2: str = "",
    line3: str = "",
) -> str:
    """Regroupe et normalise en casse titre les lignes de rue non vides (`Ligne1`, `Ligne2`, `Ligne3`)."""
    parts: list[str] = []
    for line in (line1, line2, line3):
        cleaned = normalize_address_part(line)
        if cleaned:
            parts.append(cleaned)
    return ", ".join(parts)
