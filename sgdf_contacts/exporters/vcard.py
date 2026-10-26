"""Génération vCard 3.0 (`ContactParents.vcf`) depuis `ParentContact` ou `ParentContactCard`."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from sgdf_contacts.domain import ParentContact, ParentContactCard


def escape_vcard_value(text: str) -> str:
    """Échappe les caractères spéciaux (RFC 2426 : `\\`, `;`, `,`, `\\n`) d'une valeur vCard 3.0."""
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    escaped_text = (
        normalized_text.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\n", r"\n")
    )
    return escaped_text


def format_children_with_units(children_names: str, children_units: str) -> str:
    """Associe chaque enfant à son unité respective sous la forme `Prénom Nom (Unité)`."""
    children = [child.strip() for child in children_names.split(",") if child.strip()]
    if not children:
        return ""

    units = [unit.strip() for unit in children_units.split(",") if unit.strip()]
    formatted_items: list[str] = []

    for index, child in enumerate(children):
        if index < len(units) and units[index]:
            formatted_items.append(f"{child} ({units[index]})")
        elif len(units) == 1 and units[0]:
            formatted_items.append(f"{child} ({units[0]})")
        else:
            formatted_items.append(child)

    return ", ".join(formatted_items)


def to_contact_card(contact_or_card: ParentContact | ParentContactCard) -> ParentContactCard:
    """Convertit un `ParentContact` en `ParentContactCard` ou retourne la carte telle quelle."""
    if isinstance(contact_or_card, ParentContactCard):
        return contact_or_card
    return contact_or_card.to_contact_card()


def build_parent_note(contact_or_card: ParentContact | ParentContactCard) -> str:
    """Construit le texte multi-lignes des informations complémentaires (`NOTE`) d'un parent."""
    card = to_contact_card(contact_or_card)
    note_lines: list[str] = []

    children_with_units = format_children_with_units(
        card.children_names,
        card.children_units,
    )
    if children_with_units:
        note_lines.append(f"Enfants : {children_with_units}")

    if card.member_id:
        note_lines.append(f"Numéro d'adhérent : {card.member_id}")

    if card.notes:
        note_lines.append(f"Remarques : {card.notes}")

    return "\n".join(note_lines)


def format_parent_vcard(contact_or_card: ParentContact | ParentContactCard) -> str:
    """Sérialise un `ParentContact` ou une `ParentContactCard` en bloc `VCARD` 3.0 conforme à la RFC 2426."""
    card = to_contact_card(contact_or_card)
    vcard_lines: list[str] = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escape_vcard_value(card.last_name)};{escape_vcard_value(card.first_name)};;;",
        f"FN:{escape_vcard_value(card.formatted_full_name)}",
    ]

    if card.primary_mobile_phone:
        vcard_lines.append(
            f"TEL;TYPE=CELL,VOICE,PREF:{card.primary_mobile_phone}"
        )
    if card.secondary_mobile_phone:
        vcard_lines.append(
            f"TEL;TYPE=CELL,VOICE:{card.secondary_mobile_phone}"
        )
    if card.landline_phone:
        vcard_lines.append(f"TEL;TYPE=HOME,VOICE:{card.landline_phone}")

    if card.email_address:
        vcard_lines.append(f"EMAIL;TYPE=INTERNET,HOME:{card.email_address}")

    if card.street or card.postal_code or card.city:
        vcard_lines.append(
            "ADR;TYPE=HOME:;;"
            f"{escape_vcard_value(card.street)};"
            f"{escape_vcard_value(card.city)};;"
            f"{escape_vcard_value(card.postal_code)};"
        )

    parent_note = build_parent_note(card)
    if parent_note:
        vcard_lines.append(f"NOTE:{escape_vcard_value(parent_note)}")

    if card.categories:
        category_values = ",".join(
            escape_vcard_value(category) for category in card.categories
        )
        vcard_lines.append(f"CATEGORIES:{category_values}")

    vcard_lines.append("END:VCARD")
    return "\r\n".join(vcard_lines)


def format_vcf_content(
    cards: Sequence[ParentContact | ParentContactCard],
) -> str:
    """Sérialise une séquence de `ParentContact` ou `ParentContactCard` en contenu `.vcf` complet."""
    vcard_blocks = [format_parent_vcard(card) for card in cards]
    return "\r\n".join(vcard_blocks) + ("\r\n" if vcard_blocks else "")


def write_vcf_file(
    output_path: Path,
    cards: Sequence[ParentContact | ParentContactCard],
) -> None:
    """Écrit l'ensemble des fiches parents (`ParentContact` ou `ParentContactCard`) au format vCard 3.0 UTF-8."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_content = format_vcf_content(cards)
    with output_path.open("w", encoding="utf-8", newline="") as vcf_file:
        vcf_file.write(final_content)
