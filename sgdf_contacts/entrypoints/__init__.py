"""Sous-package `entrypoints` exposant les points d'entrée CLI et l'API HTTP REST FastAPI."""

from __future__ import annotations

from sgdf_contacts.entrypoints.api import ApiSettings, app, create_app, run_server
from sgdf_contacts.entrypoints.cli_extract import main as run_extract_cli
from sgdf_contacts.entrypoints.cli_extract import run_extraction
from sgdf_contacts.entrypoints.cli_vcf import main as run_vcf_cli
from sgdf_contacts.entrypoints.cli_vcf import run_vcf_generation

__all__ = [
    "ApiSettings",
    "app",
    "create_app",
    "run_extract_cli",
    "run_extraction",
    "run_server",
    "run_vcf_cli",
    "run_vcf_generation",
]
