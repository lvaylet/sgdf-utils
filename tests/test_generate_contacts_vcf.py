"""Tests unitaires et d'intégration pour `generate_contacts_vcf.py`.

Vérifie :
1. L'échappement vCard 3.0 (RFC 2426) et l'affectation directe de l'adresse (`Rue`, `Code postal`, `Ville`).
2. L'exportation complète des coordonnées des parents (`N`, `FN` au format `Prénom Nom`,
   téléphones `CELL,VOICE,PREF`, `CELL,VOICE`, `HOME,VOICE`, `EMAIL` et `ADR`).
3. La structuration du champ `NOTE` (`Enfants : Prénom Nom (Unité), ...`,
   `Numéro d'adhérent : ...` s'il existe, `Remarques : ...` si elles existent).
4. La présence systématique des étiquettes `"SGDF"` et `"La Rochelle"`
   (`CATEGORIES:SGDF,La Rochelle`) sur 100 % des fiches.
5. La gestion explicite des erreurs (fichier absent, onglet absent, colonnes invalides)
   et la lecture seule stricte de `ContactsParents.xlsx` (empreinte SHA-256 intacte).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest
from openpyxl import Workbook

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generate_contacts_vcf import (
    PARENT_CONTACTS_HEADERS,
    PARENTS_SHEET_NAME,
    ParentContactCard,
    VcfGenerationError,
    build_parent_note,
    escape_vcard_value,
    format_children_with_units,
    format_parent_vcard,
    main,
    read_parent_contacts_excel,
    run_vcf_generation,
)


def write_synthetic_parents_workbook(
    file_path: Path,
    parent_rows: list[list[str]],
    *,
    sheet_name: str = PARENTS_SHEET_NAME,
    headers: tuple[str, ...] = PARENT_CONTACTS_HEADERS,
) -> None:
    """Crée un classeur Excel `.xlsx` de test contenant l'onglet `ContactsParents`."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_name
    worksheet.append(list(headers))
    for row in parent_rows:
        worksheet.append(row)
    workbook.save(file_path)


def test_vcard_escaping_and_direct_address_assignment() -> None:
    """Vérifie l'échappement RFC 2426 et l'affectation directe de `(street, postal_code, city)` dans `ADR`."""
    assert (
        escape_vcard_value("Ligne 1, suite ; détail\nLigne 2")
        == r"Ligne 1\, suite \; détail\nLigne 2"
    )
    assert escape_vcard_value(r"Chemin\Test") == r"Chemin\\Test"

    card_with_comma_in_street = ParentContactCard(
        last_name="Dupont",
        first_name="Jean",
        street="10 Rue Du Port, Bâtiment B",
        postal_code="17000",
        city="La Rochelle",
    )
    vcard = format_parent_vcard(card_with_comma_in_street)
    assert r"ADR;TYPE=HOME:;;10 Rue Du Port\, Bâtiment B;La Rochelle;;17000;" in vcard


def test_format_children_with_units_and_build_note() -> None:
    """Vérifie l'association enfants/unités et l'omission des rubriques vides dans `NOTE`."""
    assert (
        format_children_with_units(
            "Lucas Bernard, Chloé Bernard",
            "Louveteaux-Jeannettes, Farfadets",
        )
        == "Lucas Bernard (Louveteaux-Jeannettes), Chloé Bernard (Farfadets)"
    )
    assert (
        format_children_with_units("Léo Dupont, Emma Dupont", "Scouts-Guides")
        == "Léo Dupont (Scouts-Guides), Emma Dupont (Scouts-Guides)"
    )
    assert format_children_with_units("", "") == ""

    # Cas 1 : Parent avec enfants, numéro d'adhérent et remarques
    full_card = ParentContactCard(
        last_name="Bernard",
        first_name="Élodie",
        children_names="Lucas Bernard, Chloé Bernard",
        children_units="Scouts-Guides, Farfadets",
        member_id="987654321",
        notes="Parent Animateur Farfadet ; Enfant Lucas : Invité(e)",
    )
    full_note = build_parent_note(full_card)
    assert full_note == (
        "Enfants : Lucas Bernard (Scouts-Guides), Chloé Bernard (Farfadets)\n"
        "Numéro d'adhérent : 987654321\n"
        "Remarques : Parent Animateur Farfadet ; Enfant Lucas : Invité(e)"
    )

    # Cas 2 : Parent sans numéro d'adhérent ni remarques -> seule la ligne Enfants est présente
    simple_card = ParentContactCard(
        last_name="Martin",
        first_name="Paul",
        children_names="Tom Martin",
        children_units="Pionniers-Caravelles",
    )
    simple_note = build_parent_note(simple_card)
    assert simple_note == "Enfants : Tom Martin (Pionniers-Caravelles)"
    assert "Numéro d'adhérent" not in simple_note
    assert "Remarques" not in simple_note


def test_parent_vcard_serialization_complete_and_partial() -> None:
    """Vérifie la génération d'une entrée `VCARD` 3.0 complète et partielle."""
    full_card = ParentContactCard(
        last_name="Dupont",
        first_name="Jean-Pierre",
        primary_mobile_phone="+33612345678",
        secondary_mobile_phone="+33698765432",
        landline_phone="+33546123456",
        email_address="jean-pierre.dupont@example.fr",
        children_names="Lucas Dupont, Emma Dupont",
        children_units="Farfadets, Louveteaux-Jeannettes",
        street="12 Rue Des Mouettes",
        postal_code="17000",
        city="La Rochelle",
        member_id="123456789",
        notes="Parent Animateur Farfadet",
    )
    vcard = format_parent_vcard(full_card)
    lines = vcard.split("\r\n")

    assert lines[0] == "BEGIN:VCARD"
    assert lines[1] == "VERSION:3.0"
    assert "N:Dupont;Jean-Pierre;;;" in lines
    assert "FN:Jean-Pierre Dupont" in lines
    assert "TEL;TYPE=CELL,VOICE,PREF:+33612345678" in lines
    assert "TEL;TYPE=CELL,VOICE:+33698765432" in lines
    assert "TEL;TYPE=HOME,VOICE:+33546123456" in lines
    assert "EMAIL;TYPE=INTERNET,HOME:jean-pierre.dupont@example.fr" in lines
    assert "ADR;TYPE=HOME:;;12 Rue Des Mouettes;La Rochelle;;17000;" in lines
    assert (
        r"NOTE:Enfants : Lucas Dupont (Farfadets)\, Emma Dupont (Louveteaux-Jeannettes)"
        r"\nNuméro d'adhérent : 123456789\nRemarques : Parent Animateur Farfadet"
        in lines
    )
    assert "CATEGORIES:SGDF,La Rochelle" in lines
    assert lines[-1] == "END:VCARD"

    # Fiche avec coordonnées partielles : pas de portable secondaire, fixe, email ni adresse
    partial_card = ParentContactCard(
        last_name="Durand",
        first_name="Marie",
        primary_mobile_phone="+33600112233",
        children_names="Léo Durand",
        children_units="Compagnons",
    )
    partial_vcard = format_parent_vcard(partial_card)
    assert "FN:Marie Durand" in partial_vcard
    assert "TEL;TYPE=CELL,VOICE,PREF:+33600112233" in partial_vcard
    assert "TEL;TYPE=CELL,VOICE:" not in partial_vcard
    assert "TEL;TYPE=HOME,VOICE:" not in partial_vcard
    assert "EMAIL" not in partial_vcard
    assert "ADR" not in partial_vcard
    assert "NOTE:Enfants : Léo Durand (Compagnons)" in partial_vcard
    assert "CATEGORIES:SGDF,La Rochelle" in partial_vcard


def test_file_and_sheet_reading_errors(tmp_path: Path) -> None:
    """Vérifie la levée d'erreurs explicites en français lorsque l'entrée est invalide."""
    missing_path = tmp_path / "Absent.xlsx"
    with pytest.raises(VcfGenerationError, match="introuvable"):
        read_parent_contacts_excel(missing_path)

    exit_code = main(
        ["--input", str(missing_path), "--output", str(tmp_path / "out.vcf")]
    )
    assert exit_code == 1

    # Classeur sans l'onglet ContactsParents
    missing_sheet_path = tmp_path / "SansOnglet.xlsx"
    write_synthetic_parents_workbook(
        missing_sheet_path,
        [],
        sheet_name="AutreOnglet",
    )
    with pytest.raises(VcfGenerationError, match="absent"):
        read_parent_contacts_excel(missing_sheet_path)

    # Classeur avec en-têtes invalides
    bad_headers_path = tmp_path / "MauvaisEntetes.xlsx"
    write_synthetic_parents_workbook(
        bad_headers_path,
        [],
        headers=("Colonne1", "Colonne2"),
    )
    with pytest.raises(VcfGenerationError, match="En-têtes invalides"):
        read_parent_contacts_excel(bad_headers_path)


def test_vcf_file_generation_via_cli(tmp_path: Path) -> None:
    """Vérifie la génération de `ContactParents.vcf` de bout en bout via la CLI."""
    input_path = tmp_path / "ContactsParents.xlsx"
    output_path = tmp_path / "ContactParents.vcf"

    write_synthetic_parents_workbook(
        input_path,
        [
            [
                "Bernard",
                "Élodie",
                "+33601020304",
                "",
                "+33546001122",
                "elodie.bernard@example.fr",
                "Lucas Bernard, Chloé Bernard",
                "Scouts-Guides, Farfadets",
                "5 Avenue Coligny",
                "17000",
                "La Rochelle",
                "987654321",
                "Parent Animateur Farfadet ; Enfant Lucas : Invité(e)",
            ],
            [
                "Martin",
                "Paul",
                "+33699887766",
                "",
                "",
                "",
                "Tom Martin",
                "Pionniers-Caravelles",
                "",
                "",
                "",
                "",
                "",
            ],
        ],
    )

    exit_code = main(
        ["--input", str(input_path), "--output", str(output_path)]
    )
    assert exit_code == 0
    assert output_path.is_file()

    content = output_path.read_text(encoding="utf-8")
    assert content.count("BEGIN:VCARD") == 2
    assert content.count("END:VCARD") == 2
    assert content.count("CATEGORIES:SGDF,La Rochelle") == 2
    assert "FN:Élodie Bernard" in content
    assert "FN:Paul Martin" in content


def test_real_contacts_parents_xlsx_integration(tmp_path: Path) -> None:
    """Vérifie la génération de `ContactParents.vcf` depuis `ContactsParents.xlsx` réel."""
    input_path = PROJECT_ROOT / "ContactsParents.xlsx"
    if not input_path.is_file():
        return

    digest_before = hashlib.sha256(input_path.read_bytes()).hexdigest()
    output_path = tmp_path / "ContactParents.vcf"

    cards = run_vcf_generation(
        input_path=input_path,
        output_path=output_path,
    )

    digest_after = hashlib.sha256(input_path.read_bytes()).hexdigest()
    assert (
        digest_before == digest_after
    ), "`ContactsParents.xlsx` ne doit subir aucune modification."

    # 1. 134 parents uniques exportés
    assert len(cards) == 134

    content = output_path.read_text(encoding="utf-8")
    assert content.count("BEGIN:VCARD") == 134
    assert content.count("END:VCARD") == 134
    assert content.count("VERSION:3.0") == 134
    assert content.count("CATEGORIES:SGDF,La Rochelle") == 134
    assert content.count("NOTE:Enfants : ") == 134

    # 2. Vérifier la cohérence des champs sur chaque fiche
    for card in cards:
        assert card.last_name != card.last_name.upper()
        assert card.formatted_full_name == f"{card.first_name} {card.last_name}"
        assert card.categories == ("SGDF", "La Rochelle")
        assert card.children_names != ""
        assert card.children_units != ""
