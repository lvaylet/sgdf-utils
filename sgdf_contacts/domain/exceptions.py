"""Exceptions métier pour l'extraction et la génération des contacts des parents SGDF."""

from __future__ import annotations


class ContactExtractionError(Exception):
    """Erreur métier levée lors de la lecture ou de la validation de l'export SGDF."""


class VcfGenerationError(Exception):
    """Erreur métier levée lors de la lecture du classeur Excel ou de la génération vCard."""
