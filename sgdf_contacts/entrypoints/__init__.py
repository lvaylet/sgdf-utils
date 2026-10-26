"""Sous-package `entrypoints` exposant l'API HTTP REST FastAPI du projet `sgdf_contacts`."""

from __future__ import annotations

from sgdf_contacts.entrypoints.api import ApiSettings, app, create_app

__all__ = [
    "ApiSettings",
    "app",
    "create_app",
]
