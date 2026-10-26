"""Entités métier du domaine pour les contacts des parents de jeunes scouts SGDF."""

from __future__ import annotations

from dataclasses import dataclass, field

from sgdf_contacts.domain.constants import DEFAULT_CATEGORIES
from sgdf_contacts.domain.normalization import clean_whitespace, is_valid_mobile_phone


@dataclass(frozen=True)
class AttachedChild:
    """Représente un jeune scout rattaché à un parent."""

    first_name: str
    last_name: str
    short_unit: str
    registration_status: str

    def format_full_name(self) -> str:
        """Retourne le nom complet de l'enfant sous la forme 'Prénom Nom'."""
        return " ".join(part for part in (self.first_name, self.last_name) if part)


@dataclass
class AdultGroupProfile:
    """Représente une inscription adulte dans le groupe SGDF pour enrichir un parent."""

    last_name: str
    first_name: str
    member_id: str = ""
    roles_and_delegations: list[str] = field(default_factory=list)
    mobile_phone_1: str = ""
    mobile_phone_2: str = ""
    home_phone: str = ""
    email: str = ""
    street: str = ""
    postal_code: str = ""
    city: str = ""


@dataclass(frozen=True)
class ParentContactCard:
    """Représente la fiche d'un parent prête à être exportée au format vCard 3.0."""

    last_name: str
    first_name: str
    primary_mobile_phone: str = ""
    secondary_mobile_phone: str = ""
    landline_phone: str = ""
    email_address: str = ""
    children_names: str = ""
    children_units: str = ""
    street: str = ""
    postal_code: str = ""
    city: str = ""
    member_id: str = ""
    notes: str = ""
    categories: tuple[str, ...] = DEFAULT_CATEGORIES

    @property
    def formatted_full_name(self) -> str:
        """Retourne le nom complet affiché dans Google Contacts sous la forme 'Prénom Nom'."""
        return " ".join(part for part in (self.first_name, self.last_name) if part)


@dataclass
class ParentContact:
    """Représente la fiche consolidée et dédoublonnée d'un parent de jeune(s) scout(s)."""

    last_name: str
    first_name: str
    primary_mobile_phone: str = ""
    secondary_mobile_phone: str = ""
    landline_phone: str = ""
    email_address: str = ""
    children: list[AttachedChild] = field(default_factory=list)
    units: list[str] = field(default_factory=list)
    street: str = ""
    postal_code: str = ""
    city: str = ""
    member_id: str = ""
    notes_list: list[str] = field(default_factory=list)

    def add_child(self, child: AttachedChild) -> None:
        """Ajoute un enfant et son unité sans doublon à la fiche du parent."""
        if child not in self.children:
            self.children.append(child)
        if child.short_unit and child.short_unit not in self.units:
            self.units.append(child.short_unit)
        if child.registration_status and child.registration_status != "Inscrit(e)":
            status_note = f"Enfant {child.first_name} : {child.registration_status}"
            self.add_note(status_note)

    def add_note(self, note: str) -> None:
        """Ajoute une remarque non vide sans créer de doublon."""
        cleaned_note = clean_whitespace(note)
        if cleaned_note and cleaned_note not in self.notes_list:
            self.notes_list.append(cleaned_note)

    def merge_contact_info(
        self,
        *,
        primary_mobile: str = "",
        secondary_mobile: str = "",
        landline: str = "",
        email: str = "",
        street: str = "",
        postal_code: str = "",
        city: str = "",
        member_id: str = "",
    ) -> None:
        """Conserve la première valeur non vide pour chaque coordonnée du parent."""
        if not self.primary_mobile_phone and primary_mobile:
            self.primary_mobile_phone = primary_mobile
        elif (
            not self.secondary_mobile_phone
            and primary_mobile
            and primary_mobile != self.primary_mobile_phone
        ):
            self.secondary_mobile_phone = primary_mobile

        if (
            not self.secondary_mobile_phone
            and secondary_mobile
            and secondary_mobile != self.primary_mobile_phone
        ):
            self.secondary_mobile_phone = secondary_mobile

        if not self.landline_phone and landline:
            self.landline_phone = landline
        if not self.email_address and email:
            self.email_address = email
        if not (self.street or self.postal_code or self.city) and (
            street or postal_code or city
        ):
            self.street = street
            self.postal_code = postal_code
            self.city = city
        if not self.member_id and member_id:
            self.member_id = member_id

        self.reorganize_phones()

    def reorganize_phones(self) -> None:
        """Déplace un portable valide (+336/+337) vers portable 1 s'il est vide (priorité au fixe)."""
        if self.primary_mobile_phone:
            return

        if is_valid_mobile_phone(self.landline_phone):
            self.primary_mobile_phone = self.landline_phone
            self.landline_phone = ""
            if self.secondary_mobile_phone == self.primary_mobile_phone:
                self.secondary_mobile_phone = ""
        elif is_valid_mobile_phone(self.secondary_mobile_phone):
            self.primary_mobile_phone = self.secondary_mobile_phone
            self.secondary_mobile_phone = ""

    @property
    def waha_chat_id(self) -> str:
        """Retourne l'identifiant de conversation WhatsApp (WAHA) dérivé du portable principal."""
        phone = self.primary_mobile_phone.strip()
        if not phone:
            return ""
        digits = phone.lstrip("+")
        return f"{digits}@c.us" if digits else ""

    @property
    def children_names(self) -> str:
        """Retourne la liste dédoublonnée des enfants ('Prénom Nom') séparée par ', '."""
        labels: list[str] = []
        for child in self.children:
            label = child.format_full_name()
            if label and label not in labels:
                labels.append(label)
        return ", ".join(labels)

    @property
    def children_units(self) -> str:
        """Retourne les unités courtes des enfants dans le même ordre que les enfants eux-mêmes."""
        return ", ".join(
            child.short_unit for child in self.children if child.short_unit
        )

    @property
    def notes(self) -> str:
        """Retourne les remarques consolidées séparées par ' ; '."""
        return " ; ".join(self.notes_list)

    def to_excel_row(self) -> list[str]:
        """Convertit la fiche du parent en liste des 13 valeurs de colonnes attendues."""
        return [
            self.last_name,
            self.first_name,
            self.primary_mobile_phone,
            self.secondary_mobile_phone,
            self.landline_phone,
            self.email_address,
            self.children_names,
            self.children_units,
            self.street,
            self.postal_code,
            self.city,
            self.member_id,
            self.notes,
        ]

    def to_contact_card(
        self,
        categories: tuple[str, ...] = DEFAULT_CATEGORIES,
    ) -> ParentContactCard:
        """Convertit directement la fiche `ParentContact` en `ParentContactCard` pour l'export vCard."""
        return ParentContactCard(
            last_name=self.last_name,
            first_name=self.first_name,
            primary_mobile_phone=self.primary_mobile_phone,
            secondary_mobile_phone=self.secondary_mobile_phone,
            landline_phone=self.landline_phone,
            email_address=self.email_address,
            children_names=self.children_names,
            children_units=self.children_units,
            street=self.street,
            postal_code=self.postal_code,
            city=self.city,
            member_id=self.member_id,
            notes=self.notes,
            categories=categories,
        )
