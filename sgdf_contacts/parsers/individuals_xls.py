"""Lecture de l'export HTML/XLS `ExportIndividus.xls` et regroupement des parents SGDF."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from bs4 import BeautifulSoup

from sgdf_contacts.domain import (
    AdultGroupProfile,
    AttachedChild,
    ContactExtractionError,
    ParentContact,
    clean_whitespace,
    extract_delegation_roles,
    join_street_lines,
    normalize_address_part,
    normalize_adult_role,
    normalize_first_name,
    normalize_last_name,
    normalize_phone,
    normalize_short_unit,
    parent_sort_key,
)


def read_individuals_export_table(
    input_source: Path | bytes | bytearray | BinaryIO,
) -> tuple[list[str], list[list[str]]]:
    """Lit en lecture seule l'export HTML/XLS `ExportIndividus.xls` depuis un `Path` ou des `bytes` en mémoire."""
    if isinstance(input_source, (bytes, bytearray)):
        raw_bytes = bytes(input_source)
        source_label = "<flux en mémoire>"
    elif hasattr(input_source, "read"):
        raw_data = input_source.read()
        raw_bytes = (
            raw_data.encode("utf-8") if isinstance(raw_data, str) else bytes(raw_data)
        )
        source_label = "<flux en mémoire>"
    else:
        input_path = Path(input_source)
        source_label = str(input_path)
        if not input_path.is_file():
            raise ContactExtractionError(
                f"Le fichier d'entrée '{input_path}' est introuvable."
            )
        try:
            raw_bytes = input_path.read_bytes()
        except OSError as exc:
            raise ContactExtractionError(
                f"Impossible de lire le fichier '{input_path}' : {exc}"
            ) from exc

    document = BeautifulSoup(raw_bytes, "lxml")
    tr_elements = document.find_all("tr")
    if not tr_elements:
        raise ContactExtractionError(
            f"Aucun tableau HTML (`<tr>`) trouvé dans le fichier '{source_label}'."
        )

    headers = [
        clean_whitespace(cell.get_text())
        for cell in tr_elements[0].find_all(["th", "td"])
    ]
    if not headers or "Individu.Nom" not in headers:
        raise ContactExtractionError(
            f"En-têtes SGDF attendus (`Individu.Nom`) absents dans '{source_label}'."
        )

    data_rows: list[list[str]] = []
    column_count = len(headers)
    for tr_element in tr_elements[1:]:
        cells = [
            clean_whitespace(cell.get_text())
            for cell in tr_element.find_all("td")
        ]
        if not any(cells):
            continue
        if len(cells) < column_count:
            cells.extend([""] * (column_count - len(cells)))
        data_rows.append(cells[:column_count])

    return headers, data_rows


def build_adult_profiles_index(
    headers: list[str],
    rows: list[list[str]],
) -> dict[tuple[str, str], AdultGroupProfile]:
    """Construit un index des inscrits adultes (`Fonction.CategorieMembre != '0'`) par `(Nom, Prénom)`."""
    column_index = {col_name: idx for idx, col_name in enumerate(headers)}

    def get_cell(row: list[str], column: str) -> str:
        idx = column_index.get(column)
        return row[idx] if idx is not None and idx < len(row) else ""

    adult_profiles: dict[tuple[str, str], AdultGroupProfile] = {}
    for row in rows:
        category = get_cell(row, "Fonction.CategorieMembre")
        if category == "0":
            continue

        last_name = normalize_last_name(get_cell(row, "Individu.Nom"))
        first_name = normalize_first_name(get_cell(row, "Individu.Prenom"))
        if not last_name and not first_name:
            continue

        key = (last_name, first_name)
        profile = adult_profiles.get(key)
        if profile is None:
            profile = AdultGroupProfile(last_name=last_name, first_name=first_name)
            adult_profiles[key] = profile

        member_code = get_cell(row, "Individu.CodeAdherent")
        if not profile.member_id and member_code:
            profile.member_id = member_code

        title = get_cell(row, "IndividuCivilite.NomCourt")
        primary_role = normalize_adult_role(
            title=title,
            role_code=get_cell(row, "Fonction.Code"),
            male_label=get_cell(row, "Fonction.NomMasculin"),
            female_label=get_cell(row, "Fonction.NomFeminin"),
        )
        if primary_role and primary_role not in profile.roles_and_delegations:
            profile.roles_and_delegations.append(primary_role)

        for delegation_role in extract_delegation_roles(
            get_cell(row, "Inscription.Delegations"),
            title,
        ):
            if delegation_role not in profile.roles_and_delegations:
                profile.roles_and_delegations.append(delegation_role)

        if not profile.mobile_phone_1:
            profile.mobile_phone_1 = normalize_phone(
                get_cell(row, "Individu.TelephonePortable1")
            )
        if not profile.mobile_phone_2:
            profile.mobile_phone_2 = normalize_phone(
                get_cell(row, "Individu.TelephonePortable2")
            )
        if not profile.home_phone:
            profile.home_phone = normalize_phone(
                get_cell(row, "Individu.TelephoneDomicile")
            )
        if not profile.email:
            profile.email = (
                get_cell(row, "Individu.CourrielPersonnel")
                or get_cell(row, "Individu.CourrielDédiéSGDF")
            )
        adult_street = join_street_lines(
            get_cell(row, "Individu.Adresse.Ligne1"),
            get_cell(row, "Individu.Adresse.Ligne2"),
            get_cell(row, "Individu.Adresse.Ligne3"),
        )
        adult_postal_code = normalize_address_part(
            get_cell(row, "Individu.Adresse.CodePostal")
        )
        adult_city = normalize_address_part(
            get_cell(row, "Individu.Adresse.Municipalite")
        )
        if not (profile.street or profile.postal_code or profile.city) and (
            adult_street or adult_postal_code or adult_city
        ):
            profile.street = adult_street
            profile.postal_code = adult_postal_code
            profile.city = adult_city

    return adult_profiles


def extract_and_group_parents(
    headers: list[str],
    rows: list[list[str]],
) -> list[ParentContact]:
    """Extrait, dédoublonne, enrichit et trie par ordre alphabétique tous les parents de jeunes."""
    column_index = {col_name: idx for idx, col_name in enumerate(headers)}

    def get_cell(row: list[str], column: str) -> str:
        idx = column_index.get(column)
        return row[idx] if idx is not None and idx < len(row) else ""

    adult_profiles = build_adult_profiles_index(headers, rows)
    parents_by_key: dict[tuple[str, str], ParentContact] = {}

    for row in rows:
        if get_cell(row, "Fonction.CategorieMembre") != "0":
            continue

        child = AttachedChild(
            first_name=normalize_first_name(get_cell(row, "Individu.Prenom")),
            last_name=normalize_last_name(get_cell(row, "Individu.Nom")),
            short_unit=normalize_short_unit(
                get_cell(row, "Structure.Nom"),
                get_cell(row, "Fonction.Code"),
            ),
            registration_status=get_cell(row, "Inscriptions.Type") or "Inscrit(e)",
        )

        for prefix in ("RepresentantLegal1", "RepresentantLegal2", "RepresentantLegal3"):
            parent_last_name = normalize_last_name(get_cell(row, f"{prefix}.Nom"))
            parent_first_name = normalize_first_name(get_cell(row, f"{prefix}.Prenom"))
            if not parent_last_name and not parent_first_name:
                continue

            parent_key = (parent_last_name, parent_first_name)
            contact = parents_by_key.get(parent_key)
            if contact is None:
                contact = ParentContact(
                    last_name=parent_last_name,
                    first_name=parent_first_name,
                )
                parents_by_key[parent_key] = contact

            parent_email = (
                get_cell(row, f"{prefix}.CourrielPersonnel")
                or get_cell(row, f"{prefix}.CourrielDédiéSGDF")
            )
            parent_street = join_street_lines(
                get_cell(row, f"{prefix}.Adresse.Ligne1"),
                get_cell(row, f"{prefix}.Adresse.Ligne2"),
                get_cell(row, f"{prefix}.Adresse.Ligne3"),
            )
            parent_postal_code = normalize_address_part(
                get_cell(row, f"{prefix}.Adresse.CodePostal")
            )
            parent_city = normalize_address_part(
                get_cell(row, f"{prefix}.Adresse.Municipalite")
            )

            contact.merge_contact_info(
                primary_mobile=normalize_phone(
                    get_cell(row, f"{prefix}.TelephonePortable1")
                ),
                secondary_mobile=normalize_phone(
                    get_cell(row, f"{prefix}.TelephonePortable2")
                ),
                landline=normalize_phone(
                    get_cell(row, f"{prefix}.TelephoneDomicile")
                ),
                email=parent_email,
                street=parent_street,
                postal_code=parent_postal_code,
                city=parent_city,
                member_id=get_cell(row, f"{prefix}.CodeAdherent"),
            )
            contact.add_child(child)

    # Enrichissement avec l'index des profils adultes inscrits dans le groupe
    for parent_key, contact in parents_by_key.items():
        adult_profile = adult_profiles.get(parent_key)
        if adult_profile is None:
            continue

        contact.merge_contact_info(
            primary_mobile=adult_profile.mobile_phone_1,
            secondary_mobile=adult_profile.mobile_phone_2,
            landline=adult_profile.home_phone,
            email=adult_profile.email,
            street=adult_profile.street,
            postal_code=adult_profile.postal_code,
            city=adult_profile.city,
            member_id=adult_profile.member_id,
        )

        # Insérer les rôles adultes en tête des remarques (avant les statuts d'inscription des enfants)
        existing_notes = list(contact.notes_list)
        contact.notes_list.clear()
        for role in adult_profile.roles_and_delegations:
            contact.add_note(role)
        for child_note in existing_notes:
            contact.add_note(child_note)

    return sorted(parents_by_key.values(), key=parent_sort_key)
