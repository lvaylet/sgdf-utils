"""Dépôt de persistance (`ParentContactRepository`), calcul de différentiel (`ImportDiffReport`) et requêtage."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO

from sqlalchemy import delete, or_
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from sgdf_contacts.domain import (
    DEFAULT_CATEGORIES,
    AttachedChild,
    ParentContact,
    is_valid_mobile_phone,
    normalize_first_name,
    normalize_last_name,
    normalize_phone,
    normalize_short_unit,
    parent_sort_key,
)
from sgdf_contacts.exporters import (
    format_vcf_content,
    write_parent_contacts_workbook,
    write_vcf_file,
)
from sgdf_contacts.parsers import (
    extract_and_group_parents,
    read_individuals_export_table,
)
from sgdf_contacts.persistence.models import (
    ChildRecord,
    ParentChildLink,
    ParentRecord,
    init_db,
    utc_now,
)


@dataclass(frozen=True)
class FieldChange:
    """Représente la modification d'un champ sur une fiche parent lors d'un import."""

    old_value: Any
    new_value: Any


@dataclass(frozen=True)
class ParentUpdateDiff:
    """Représente un parent existant mis à jour lors d'un import avec le détail des champs modifiés."""

    parent: ParentContact
    changes: dict[str, FieldChange]


@dataclass
class ImportDiffReport:
    """Rapport de différentiel produit par l'import transactionnel des contacts parents."""

    created: list[ParentContact] = field(default_factory=list)
    updated: list[ParentUpdateDiff] = field(default_factory=list)
    unchanged: list[ParentContact] = field(default_factory=list)
    deactivated: list[ParentContact] = field(default_factory=list)


class ParentContactRepository:
    """Gère la persistance transactionnelle, le calcul de différentiel et le requêtage des parents."""

    def __init__(self, engine: Engine) -> None:
        """Initialise le dépôt avec un moteur SQLAlchemy/SQLModel et garantit l'existence des tables."""
        self.engine = engine
        init_db(self.engine)

    @staticmethod
    def _load_ordered_children_map(
        session: Session,
        parent_ids: Sequence[int],
    ) -> dict[int, list[AttachedChild]]:
        """Charge les enfants rattachés à chaque parent en respectant l'ordre de `ParentChildLink.position`."""
        result: dict[int, list[AttachedChild]] = {pid: [] for pid in parent_ids}
        if not parent_ids:
            return result

        statement = (
            select(ParentChildLink, ChildRecord)
            .join(ChildRecord, ParentChildLink.child_id == ChildRecord.id)
            .where(ParentChildLink.parent_id.in_(parent_ids))
            .order_by(ParentChildLink.parent_id, ParentChildLink.position, ChildRecord.id)
        )
        for link, child_record in session.exec(statement):
            if link.parent_id is not None:
                result.setdefault(link.parent_id, []).append(child_record.to_domain())
        return result

    @staticmethod
    def _compute_parent_changes(
        record: ParentRecord,
        existing_children: Sequence[AttachedChild],
        incoming: ParentContact,
    ) -> dict[str, FieldChange]:
        """Compare champ par champ l'état persisté d'un parent avec la fiche entrante."""
        changes: dict[str, FieldChange] = {}

        scalar_comparisons = (
            ("member_id", record.member_id, incoming.member_id),
            ("last_name", record.last_name, incoming.last_name),
            ("first_name", record.first_name, incoming.first_name),
            (
                "primary_mobile_phone",
                record.primary_mobile_phone,
                incoming.primary_mobile_phone,
            ),
            (
                "secondary_mobile_phone",
                record.secondary_mobile_phone,
                incoming.secondary_mobile_phone,
            ),
            ("landline_phone", record.landline_phone, incoming.landline_phone),
            ("email_address", record.email_address, incoming.email_address),
            ("street", record.street, incoming.street),
            ("postal_code", record.postal_code, incoming.postal_code),
            ("city", record.city, incoming.city),
            ("notes", record.notes, incoming.notes),
        )
        for field_name, old_val, new_val in scalar_comparisons:
            if old_val != new_val:
                changes[field_name] = FieldChange(old_value=old_val, new_value=new_val)

        old_children_list = list(existing_children)
        new_children_list = list(incoming.children)
        if old_children_list != new_children_list:
            changes["children"] = FieldChange(
                old_value=old_children_list,
                new_value=new_children_list,
            )

        old_children_names = ", ".join(
            child.format_full_name()
            for child in old_children_list
            if child.format_full_name()
        )
        if old_children_names != incoming.children_names:
            changes["children_names"] = FieldChange(
                old_value=old_children_names,
                new_value=incoming.children_names,
            )

        old_children_units = ", ".join(
            child.short_unit for child in old_children_list if child.short_unit
        )
        if old_children_units != incoming.children_units:
            changes["children_units"] = FieldChange(
                old_value=old_children_units,
                new_value=incoming.children_units,
            )

        if not record.is_active:
            changes["is_active"] = FieldChange(old_value=False, new_value=True)

        return changes

    @staticmethod
    def _upsert_children_and_links(
        session: Session,
        parent_record: ParentRecord,
        incoming_children: Sequence[AttachedChild],
        children_by_key: dict[tuple[str, str], ChildRecord],
    ) -> list[AttachedChild]:
        """Crée ou met à jour les enfants rattachés et recrée les liens ordonnés `ParentChildLink`."""
        assert parent_record.id is not None

        session.exec(
            delete(ParentChildLink).where(
                ParentChildLink.parent_id == parent_record.id
            )
        )

        ordered_domain_children: list[AttachedChild] = []
        seen_child_ids: set[int] = set()

        for position, child in enumerate(incoming_children):
            child_key = (child.last_name, child.first_name)
            child_record = children_by_key.get(child_key)
            if child_record is None:
                child_record = ChildRecord(
                    first_name=child.first_name,
                    last_name=child.last_name,
                    short_unit=child.short_unit,
                    registration_status=child.registration_status,
                )
                session.add(child_record)
                session.flush()
                children_by_key[child_key] = child_record
            else:
                if child_record.short_unit != child.short_unit:
                    child_record.short_unit = child.short_unit
                if child_record.registration_status != child.registration_status:
                    child_record.registration_status = child.registration_status
                session.add(child_record)
                session.flush()

            assert child_record.id is not None
            if child_record.id not in seen_child_ids:
                seen_child_ids.add(child_record.id)
                session.add(
                    ParentChildLink(
                        parent_id=parent_record.id,
                        child_id=child_record.id,
                        position=position,
                    )
                )
                ordered_domain_children.append(child_record.to_domain())

        return ordered_domain_children

    def sync_parents(self, parents: Sequence[ParentContact]) -> ImportDiffReport:
        """Synchronise de façon transactionnelle une liste de `ParentContact` et retourne `ImportDiffReport`."""
        report = ImportDiffReport()
        now = utc_now()

        with Session(self.engine) as session:
            existing_parents = list(session.exec(select(ParentRecord)).all())
            existing_children = list(session.exec(select(ChildRecord)).all())

            parent_ids = [p.id for p in existing_parents if p.id is not None]
            children_map = self._load_ordered_children_map(session, parent_ids)

            parents_by_member_id: dict[str, ParentRecord] = {
                p.member_id: p for p in existing_parents if p.member_id
            }
            parents_by_name: dict[tuple[str, str], ParentRecord] = {
                (p.last_name, p.first_name): p for p in existing_parents
            }
            children_by_key: dict[tuple[str, str], ChildRecord] = {
                (c.last_name, c.first_name): c for c in existing_children
            }

            matched_parent_ids: set[int] = set()

            for incoming in parents:
                matched_record: ParentRecord | None = None
                if incoming.member_id and incoming.member_id in parents_by_member_id:
                    candidate = parents_by_member_id[incoming.member_id]
                    if candidate.id not in matched_parent_ids:
                        matched_record = candidate

                if matched_record is None:
                    candidate = parents_by_name.get(
                        (incoming.last_name, incoming.first_name)
                    )
                    if candidate is not None and candidate.id not in matched_parent_ids:
                        matched_record = candidate

                if matched_record is None:
                    new_record = ParentRecord(
                        member_id=incoming.member_id,
                        last_name=incoming.last_name,
                        first_name=incoming.first_name,
                        primary_mobile_phone=incoming.primary_mobile_phone,
                        secondary_mobile_phone=incoming.secondary_mobile_phone,
                        landline_phone=incoming.landline_phone,
                        email_address=incoming.email_address,
                        street=incoming.street,
                        postal_code=incoming.postal_code,
                        city=incoming.city,
                        notes=incoming.notes,
                        has_whatsapp=None,
                        first_seen_at=now,
                        updated_at=now,
                        is_active=True,
                    )
                    session.add(new_record)
                    session.flush()
                    assert new_record.id is not None
                    matched_parent_ids.add(new_record.id)
                    parents_by_name[(new_record.last_name, new_record.first_name)] = (
                        new_record
                    )
                    if new_record.member_id:
                        parents_by_member_id[new_record.member_id] = new_record

                    ordered_children = self._upsert_children_and_links(
                        session,
                        new_record,
                        incoming.children,
                        children_by_key,
                    )
                    report.created.append(new_record.to_domain(ordered_children))
                else:
                    assert matched_record.id is not None
                    matched_parent_ids.add(matched_record.id)
                    old_children = children_map.get(matched_record.id, [])
                    changes = self._compute_parent_changes(
                        matched_record,
                        old_children,
                        incoming,
                    )

                    if not changes:
                        # Synchronise malgré tout les attributs des enfants partagés si nécessaire
                        ordered_children = self._upsert_children_and_links(
                            session,
                            matched_record,
                            incoming.children,
                            children_by_key,
                        )
                        report.unchanged.append(
                            matched_record.to_domain(ordered_children)
                        )
                    else:
                        old_name_key = (
                            matched_record.last_name,
                            matched_record.first_name,
                        )
                        old_member_id = matched_record.member_id

                        matched_record.member_id = incoming.member_id
                        matched_record.last_name = incoming.last_name
                        matched_record.first_name = incoming.first_name
                        matched_record.primary_mobile_phone = (
                            incoming.primary_mobile_phone
                        )
                        matched_record.secondary_mobile_phone = (
                            incoming.secondary_mobile_phone
                        )
                        matched_record.landline_phone = incoming.landline_phone
                        matched_record.email_address = incoming.email_address
                        matched_record.street = incoming.street
                        matched_record.postal_code = incoming.postal_code
                        matched_record.city = incoming.city
                        matched_record.notes = incoming.notes
                        matched_record.is_active = True
                        matched_record.updated_at = now
                        session.add(matched_record)
                        session.flush()

                        if old_name_key != (
                            matched_record.last_name,
                            matched_record.first_name,
                        ):
                            parents_by_name.pop(old_name_key, None)
                            parents_by_name[
                                (matched_record.last_name, matched_record.first_name)
                            ] = matched_record
                        if old_member_id and old_member_id != matched_record.member_id:
                            parents_by_member_id.pop(old_member_id, None)
                        if matched_record.member_id:
                            parents_by_member_id[matched_record.member_id] = (
                                matched_record
                            )

                        ordered_children = self._upsert_children_and_links(
                            session,
                            matched_record,
                            incoming.children,
                            children_by_key,
                        )
                        updated_domain = matched_record.to_domain(ordered_children)
                        report.updated.append(
                            ParentUpdateDiff(parent=updated_domain, changes=changes)
                        )

            # Désactivation douce des parents précédemment actifs mais absents du nouvel import
            for existing in existing_parents:
                if (
                    existing.id is not None
                    and existing.id not in matched_parent_ids
                    and existing.is_active
                ):
                    existing.is_active = False
                    existing.updated_at = now
                    session.add(existing)
                    old_children = children_map.get(existing.id, [])
                    report.deactivated.append(existing.to_domain(old_children))

            session.commit()

        report.created.sort(key=parent_sort_key)
        report.updated.sort(key=lambda item: parent_sort_key(item.parent))
        report.unchanged.sort(key=parent_sort_key)
        report.deactivated.sort(key=parent_sort_key)
        return report

    def import_individuals_xls(
        self,
        source: Path | bytes | BinaryIO,
    ) -> ImportDiffReport:
        """Extrait les parents d'un export `ExportIndividus.xls` (chemin ou flux mémoire) et les synchronise en base."""
        headers, rows = read_individuals_export_table(source)
        parents = extract_and_group_parents(headers, rows)
        return self.sync_parents(parents)

    def set_whatsapp_status(
        self,
        last_name: str,
        first_name: str,
        has_whatsapp: bool | None,
    ) -> bool:
        """Met à jour l'indicateur externe `has_whatsapp` d'un parent sans modifier ses coordonnées."""
        norm_last = normalize_last_name(last_name)
        norm_first = normalize_first_name(first_name)

        with Session(self.engine) as session:
            statement = select(ParentRecord).where(
                ParentRecord.last_name == norm_last,
                ParentRecord.first_name == norm_first,
            )
            record = session.exec(statement).first()
            if record is None:
                return False
            record.has_whatsapp = has_whatsapp
            record.updated_at = utc_now()
            session.add(record)
            session.commit()
            return True

    def get_parent_record(
        self,
        last_name: str,
        first_name: str,
    ) -> ParentRecord | None:
        """Retourne l'enregistrement brut `ParentRecord` pour un couple `(last_name, first_name)`."""
        norm_last = normalize_last_name(last_name)
        norm_first = normalize_first_name(first_name)

        with Session(self.engine) as session:
            statement = select(ParentRecord).where(
                ParentRecord.last_name == norm_last,
                ParentRecord.first_name == norm_first,
            )
            return session.exec(statement).first()

    def list_active_parents(self) -> list[ParentContact]:
        """Retourne tous les parents actifs (`is_active=True`) triés selon l'ordre alphabétique français."""
        return self.filter_parents(include_inactive=False)

    def filter_parents(
        self,
        *,
        short_unit: str | None = None,
        registration_status: str | None = None,
        has_valid_mobile: bool | None = None,
        include_inactive: bool = False,
    ) -> list[ParentContact]:
        """Filtre les parents selon l'unité d'enfant, le statut d'inscription et/ou la présence d'un portable valide."""
        normalized_unit = normalize_short_unit(short_unit) if short_unit else None
        normalized_status = (
            registration_status.strip() if registration_status is not None else None
        )

        with Session(self.engine) as session:
            statement = select(ParentRecord)
            if not include_inactive:
                statement = statement.where(ParentRecord.is_active == True)

            records = list(session.exec(statement).all())
            parent_ids = [r.id for r in records if r.id is not None]
            children_map = self._load_ordered_children_map(session, parent_ids)

            results: list[ParentContact] = []
            for record in records:
                if record.id is None:
                    continue
                domain_children = children_map.get(record.id, [])

                if normalized_unit is not None and not any(
                    normalize_short_unit(child.short_unit) == normalized_unit
                    or child.short_unit.casefold() == short_unit.strip().casefold()
                    for child in domain_children
                ):
                    continue

                if normalized_status is not None and not any(
                    child.registration_status.casefold()
                    == normalized_status.casefold()
                    for child in domain_children
                ):
                    continue

                if has_valid_mobile is not None:
                    has_mobile = is_valid_mobile_phone(
                        record.primary_mobile_phone
                    ) or is_valid_mobile_phone(record.secondary_mobile_phone)
                    if has_mobile != has_valid_mobile:
                        continue

                results.append(record.to_domain(domain_children))

        results.sort(key=parent_sort_key)
        return results

    def find_by_phone(
        self,
        phone: str,
        *,
        include_inactive: bool = False,
    ) -> ParentContact | None:
        """Recherche un parent par numéro de téléphone (`primary_mobile_phone`, `secondary_mobile_phone`, `landline_phone`)."""
        cleaned_input = phone.strip()
        if not cleaned_input:
            return None

        normalized = normalize_phone(cleaned_input)
        candidate_phones = {cleaned_input}
        if normalized:
            candidate_phones.add(normalized)
        if cleaned_input.isdigit() and cleaned_input.startswith("33"):
            candidate_phones.add(f"+{cleaned_input}")

        with Session(self.engine) as session:
            statement = select(ParentRecord).where(
                or_(
                    ParentRecord.primary_mobile_phone.in_(candidate_phones),
                    ParentRecord.secondary_mobile_phone.in_(candidate_phones),
                    ParentRecord.landline_phone.in_(candidate_phones),
                )
            )
            if not include_inactive:
                statement = statement.where(ParentRecord.is_active == True)

            records = list(session.exec(statement).all())
            if not records:
                return None

            parent_ids = [r.id for r in records if r.id is not None]
            children_map = self._load_ordered_children_map(session, parent_ids)
            domains = [
                r.to_domain(children_map.get(r.id, []))
                for r in records
                if r.id is not None
            ]
            domains.sort(key=parent_sort_key)
            return domains[0] if domains else None

    def export_vcf(
        self,
        output_path: Path | None = None,
        *,
        categories: tuple[str, ...] = DEFAULT_CATEGORIES,
    ) -> str:
        """Régénère `ContactParents.vcf` directement depuis les parents actifs stockés en base SQLite."""
        active_parents = self.list_active_parents()
        cards = [
            parent.to_contact_card(categories=categories)
            for parent in active_parents
        ]
        vcf_content = format_vcf_content(cards)
        if output_path is not None:
            write_vcf_file(Path(output_path), cards)
        return vcf_content

    def export_excel(
        self,
        output_path: Path | BinaryIO | None = None,
        *,
        source_headers: list[str] | None = None,
        source_rows: list[list[str]] | None = None,
    ) -> bytes:
        """Régénère `ContactsParents.xlsx` directement depuis les parents actifs stockés en base SQLite."""
        active_parents = self.list_active_parents()
        return write_parent_contacts_workbook(
            output_path=output_path,
            source_headers=source_headers,
            source_rows=source_rows,
            parent_contacts=active_parents,
        )
