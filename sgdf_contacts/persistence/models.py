"""Modèles de persistance SQLModel (`parents`, `children`, `parent_child_links`) et moteur SQLite."""

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import UniqueConstraint, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Relationship, SQLModel, create_engine

from sgdf_contacts.domain import AttachedChild, ParentContact


def utc_now() -> datetime:
    """Retourne l'horodatage courant en UTC."""
    return datetime.now(UTC)


class ParentChildLink(SQLModel, table=True):
    """Table de liaison N-N entre `parents` et `children` avec préservation de l'ordre d'apparition."""

    __tablename__ = "parent_child_links"

    parent_id: int | None = Field(
        default=None,
        foreign_key="parents.id",
        primary_key=True,
    )
    child_id: int | None = Field(
        default=None,
        foreign_key="children.id",
        primary_key=True,
    )
    position: int = Field(default=0)


class ChildRecord(SQLModel, table=True):
    """Enregistrement persistant d'un jeune scout rattaché à un ou plusieurs parents."""

    __tablename__ = "children"
    __table_args__ = (
        UniqueConstraint(
            "last_name",
            "first_name",
            name="uq_children_last_first_name",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    short_unit: str = Field(default="", index=True)
    registration_status: str = Field(default="", index=True)

    parents: list["ParentRecord"] = Relationship(
        back_populates="children",
        link_model=ParentChildLink,
    )

    def to_domain(self) -> AttachedChild:
        """Convertit l'enregistrement en entité `AttachedChild` immuable du domaine."""
        return AttachedChild(
            first_name=self.first_name,
            last_name=self.last_name,
            short_unit=self.short_unit,
            registration_status=self.registration_status,
        )


class ParentRecord(SQLModel, table=True):
    """Enregistrement persistant d'un parent de jeune(s) scout(s) SGDF."""

    __tablename__ = "parents"
    __table_args__ = (
        UniqueConstraint(
            "last_name",
            "first_name",
            name="uq_parents_last_first_name",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    member_id: str = Field(default="", index=True)
    last_name: str = Field(index=True)
    first_name: str = Field(index=True)
    primary_mobile_phone: str = Field(default="", index=True)
    secondary_mobile_phone: str = Field(default="", index=True)
    landline_phone: str = Field(default="", index=True)
    email_address: str = Field(default="")
    street: str = Field(default="")
    postal_code: str = Field(default="")
    city: str = Field(default="")
    notes: str = Field(default="")
    has_whatsapp: bool | None = Field(default=None, nullable=True)
    first_seen_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    is_active: bool = Field(default=True, index=True)

    children: list[ChildRecord] = Relationship(
        back_populates="parents",
        link_model=ParentChildLink,
    )

    def to_domain(
        self,
        ordered_children: Sequence[AttachedChild] | None = None,
    ) -> ParentContact:
        """Reconstruit fidèlement l'entité `ParentContact` du domaine à partir de l'enregistrement."""
        domain_children = (
            list(ordered_children)
            if ordered_children is not None
            else [child.to_domain() for child in self.children]
        )
        units: list[str] = []
        for child in domain_children:
            if child.short_unit and child.short_unit not in units:
                units.append(child.short_unit)

        notes_list = [
            part.strip() for part in self.notes.split(" ; ") if part.strip()
        ]
        return ParentContact(
            last_name=self.last_name,
            first_name=self.first_name,
            primary_mobile_phone=self.primary_mobile_phone,
            secondary_mobile_phone=self.secondary_mobile_phone,
            landline_phone=self.landline_phone,
            email_address=self.email_address,
            children=domain_children,
            units=units,
            street=self.street,
            postal_code=self.postal_code,
            city=self.city,
            member_id=self.member_id,
            notes_list=notes_list,
        )


def _configure_sqlite_pragmas(engine: Engine) -> None:
    """Active automatiquement `PRAGMA journal_mode=WAL;` et `PRAGMA foreign_keys=ON;` sur SQLite."""
    if engine.dialect.name != "sqlite":
        return

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()


def create_db_engine(
    database_url: str | Path = "sqlite:///sgdf_contacts.db",
    *,
    echo: bool = False,
) -> Engine:
    """Crée un moteur SQLAlchemy/SQLModel et configure automatiquement les pragmas SQLite."""
    if isinstance(database_url, Path):
        resolved_path = database_url.resolve()
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{resolved_path}"
    else:
        url = str(database_url)
        if not ("://" in url or url.startswith("sqlite:")):
            resolved_path = Path(url).resolve()
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            url = f"sqlite:///{resolved_path}"

    if url.startswith("sqlite"):
        is_memory = url in ("sqlite://", "sqlite:///:memory:") or ":memory:" in url
        if is_memory:
            engine = create_engine(
                url,
                echo=echo,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            engine = create_engine(
                url,
                echo=echo,
                connect_args={"check_same_thread": False},
            )
    else:
        engine = create_engine(url, echo=echo)
    _configure_sqlite_pragmas(engine)
    return engine


def init_db(engine: Engine) -> None:
    """Initialise le schéma de base de données (`parents`, `children`, `parent_child_links`)."""
    _configure_sqlite_pragmas(engine)
    SQLModel.metadata.create_all(engine)
