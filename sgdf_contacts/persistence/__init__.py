"""Sous-package `persistence` pour le stockage SQLite/SQLModel et le calcul de différentiel d'import."""

from __future__ import annotations

from sgdf_contacts.persistence.models import (
    ChildRecord,
    ParentChildLink,
    ParentRecord,
    create_db_engine,
    init_db,
)
from sgdf_contacts.persistence.repository import (
    FieldChange,
    ImportDiffReport,
    ParentContactRepository,
    ParentUpdateDiff,
)

__all__ = [
    "ChildRecord",
    "FieldChange",
    "ImportDiffReport",
    "ParentChildLink",
    "ParentContactRepository",
    "ParentRecord",
    "ParentUpdateDiff",
    "create_db_engine",
    "init_db",
]
