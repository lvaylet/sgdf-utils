"""Tests automatisés de l'environnement de développement éphémère SGDF La Rochelle.

Ce module vérifie :
1. La présence et l'isolation de l'interpréteur Python 3 et des outils requis.
2. L'importation sans erreur de toutes les bibliothèques Python nécessaires aux scripts SGDF.
3. La parité stricte entre les définitions déclaratives `flake.nix` et `devbox.json`.
4. Le fonctionnement de la matrice de décision `.envrc` selon `ENV_TOOL`.
5. La lecture seule et l'intégrité du fichier d'export SGDF (`ExportIndividus.xls`).
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_PYTHON_MODULES = (
    "pandas",
    "bs4",
    "lxml",
    "xlrd",
    "openpyxl",
    "sqlmodel",
    "sqlalchemy",
    "fastapi",
    "uvicorn",
    "python_multipart",
    "httpx",
    "pytest",
)

EXPECTED_NIX_PACKAGES = (
    "pandas",
    "beautifulsoup4",
    "lxml",
    "xlrd",
    "openpyxl",
    "sqlmodel",
    "sqlalchemy",
    "fastapi",
    "uvicorn",
    "python-multipart",
    "httpx",
    "pytest",
    "ruff",
)


def compute_sha256_digest(file_path: Path) -> str:
    """Calcule l'empreinte SHA-256 d'un fichier sans le modifier."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as input_stream:
        for chunk in iter(lambda: input_stream.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def test_python_version_and_isolation() -> None:
    """Vérifie que Python 3 est actif et provient d'un environnement isolé (Nix ou Devbox)."""
    assert sys.version_info >= (3, 10), "Python 3.10 ou supérieur est requis."

    executable_path = Path(sys.executable).resolve()
    path_str = str(executable_path)
    is_isolated = ("/nix/store/" in path_str) or (".devbox" in path_str)
    assert is_isolated, (
        f"L'interpréteur Python ({path_str}) doit provenir du store Nix ou de Devbox."
    )


def test_sgdf_libraries_import() -> None:
    """Vérifie que toutes les bibliothèques requises pour les scripts SGDF sont importables."""
    for module_name in REQUIRED_PYTHON_MODULES:
        imported_module = importlib.import_module(module_name)
        assert imported_module is not None, f"Échec de l'importation du module {module_name}."


def test_cli_tools_availability() -> None:
    """Vérifie que les exécutables `pytest` et `ruff` sont disponibles dans le PATH."""
    for tool_name in ("python3", "pytest", "ruff"):
        tool_path = shutil.which(tool_name)
        assert tool_path is not None, f"L'outil '{tool_name}' doit être disponible dans le PATH."


def test_flake_nix_compliance_and_lockfile() -> None:
    """Vérifie que `flake.nix` et `flake.lock` existent et déclarent tous les paquets requis."""
    flake_path = PROJECT_ROOT / "flake.nix"
    lock_path = PROJECT_ROOT / "flake.lock"

    assert flake_path.is_file(), "Le fichier `flake.nix` doit exister à la racine."
    assert lock_path.is_file(), "Le fichier `flake.lock` doit exister à la racine."

    flake_content = flake_path.read_text(encoding="utf-8")
    assert "python3.withPackages" in flake_content, (
        "`flake.nix` doit utiliser `python3.withPackages` sans pip ni .venv."
    )
    for package_name in EXPECTED_NIX_PACKAGES:
        assert package_name in flake_content, (
            f"Le paquet '{package_name}' doit figurer dans `flake.nix`."
        )

    assert "SGDF" in flake_content and "Environnement" in flake_content, (
        "`flake.nix` doit contenir une description et un message d'accueil en français."
    )


def test_devbox_json_compliance_and_parity() -> None:
    """Vérifie que `devbox.json` est valide et en parité stricte à 100 % avec `flake.nix`."""
    devbox_path = PROJECT_ROOT / "devbox.json"
    assert devbox_path.is_file(), "Le fichier `devbox.json` doit exister à la racine."

    devbox_data = json.loads(devbox_path.read_text(encoding="utf-8"))
    devbox_packages = devbox_data.get("packages", [])
    packages_text = " ".join(devbox_packages)

    assert any(pkg.startswith("python3") for pkg in devbox_packages), (
        "`devbox.json` doit déclarer l'interpréteur `python3`."
    )
    for package_name in EXPECTED_NIX_PACKAGES:
        assert package_name in packages_text, (
            f"Le paquet '{package_name}' doit être présent dans `devbox.json` pour assurer la parité."
        )

    shell_config = devbox_data.get("shell", {})
    welcome_commands = "\n".join(shell_config.get("init_hook", []))
    assert "Environnement" in welcome_commands, (
        "Le message d'accueil `init_hook` de `devbox.json` doit être rédigé en français."
    )

    devbox_scripts = shell_config.get("scripts", {})
    for script_name in ("check_environment", "test", "check_quality"):
        assert script_name in devbox_scripts, (
            f"Le script '{script_name}' doit être défini dans `devbox.json`."
        )


def test_envrc_decision_matrix(tmp_path: Path) -> None:
    """Vérifie la logique de sélection `.envrc` selon `ENV_TOOL` et les outils présents."""
    envrc_path = PROJECT_ROOT / ".envrc"
    assert envrc_path.is_file(), "Le fichier `.envrc` doit exister à la racine."

    envrc_content = envrc_path.read_text(encoding="utf-8")
    assert "ENV_TOOL" in envrc_content
    assert "use flake" in envrc_content
    assert "devbox generate direnv" in envrc_content

    harness_script = tmp_path / "envrc_harness.sh"
    harness_script.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
source_env_if_exists() { :; }
watch_file() { :; }
has() {
    local tool="$1"
    if [[ "$tool" == "nix" && "${MOCK_NIX:-0}" == "1" ]]; then return 0; fi
    if [[ "$tool" == "devbox" && "${MOCK_DEVBOX:-0}" == "1" ]]; then return 0; fi
    return 1
}
use() {
    echo "ACTIVE_ACTION=flake:$*"
}
devbox() {
    if [[ "$1" == "generate" && "$2" == "direnv" ]]; then
        echo "echo ACTIVE_ACTION=devbox"
    fi
}
source "$ENVRC_PATH"
""",
        encoding="utf-8",
    )

    def run_scenario(
        env_tool: str | None,
        mock_nix: bool,
        mock_devbox: bool,
    ) -> subprocess.CompletedProcess[str]:
        test_env = os.environ.copy()
        test_env["ENVRC_PATH"] = str(envrc_path)
        test_env["MOCK_NIX"] = "1" if mock_nix else "0"
        test_env["MOCK_DEVBOX"] = "1" if mock_devbox else "0"
        if env_tool is None:
            test_env.pop("ENV_TOOL", None)
        else:
            test_env["ENV_TOOL"] = env_tool

        return subprocess.run(
            ["bash", str(harness_script)],
            env=test_env,
            capture_output=True,
            text=True,
            check=False,
        )

    # 1. Mode par défaut (auto) avec Nix et Devbox présents -> Priorité à flake.nix
    result_auto_both = run_scenario(None, mock_nix=True, mock_devbox=True)
    assert result_auto_both.returncode == 0
    assert "ACTIVE_ACTION=flake:flake" in result_auto_both.stdout
    assert "ACTIVE_ACTION=devbox" not in result_auto_both.stdout

    # 2. Mode par défaut (auto) avec uniquement Devbox présent -> Repli sur devbox.json
    result_auto_devbox = run_scenario(None, mock_nix=False, mock_devbox=True)
    assert result_auto_devbox.returncode == 0
    assert "ACTIVE_ACTION=devbox" in result_auto_devbox.stdout

    # 3. Bascule explicite vers devbox quand les deux sont présents
    result_force_devbox = run_scenario("devbox", mock_nix=True, mock_devbox=True)
    assert result_force_devbox.returncode == 0
    assert "ACTIVE_ACTION=devbox" in result_force_devbox.stdout
    assert "ACTIVE_ACTION=flake:flake" not in result_force_devbox.stdout

    # 4. Bascule explicite vers flake quand les deux sont présents
    result_force_flake = run_scenario("flake", mock_nix=True, mock_devbox=True)
    assert result_force_flake.returncode == 0
    assert "ACTIVE_ACTION=flake:flake" in result_force_flake.stdout

    # 5. Absence simultanée de Nix et Devbox -> Message d'erreur en français sans planter le shell
    result_no_tool = run_scenario("auto", mock_nix=False, mock_devbox=False)
    combined_output = result_no_tool.stdout + result_no_tool.stderr
    assert "Erreur" in combined_output or "aucun" in combined_output.lower()

    # 6. Valeur invalide de ENV_TOOL -> Message d'erreur en français
    result_invalid = run_scenario("unknown", mock_nix=True, mock_devbox=True)
    invalid_output = result_invalid.stdout + result_invalid.stderr
    assert "ENV_TOOL" in invalid_output


def test_gitignore_data_protection() -> None:
    """Vérifie que `.gitignore` protège les fichiers d'export SGDF et les caches locaux."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    assert gitignore_path.is_file(), "Le fichier `.gitignore` doit exister à la racine."

    gitignore_content = gitignore_path.read_text(encoding="utf-8")
    for required_pattern in (
        "*.xls",
        "*.xlsx",
        "*.csv",
        "*.db",
        "ExportIndividus*",
        ".direnv/",
        ".devbox/",
        ".envrc.local",
    ):
        assert required_pattern in gitignore_content, (
            f"Le motif '{required_pattern}' doit figurer dans `.gitignore`."
        )


def test_individuals_export_read_only() -> None:
    """Vérifie que `ExportIndividus.xls` peut être analysé en lecture seule sans altération."""
    export_path = PROJECT_ROOT / "ExportIndividus.xls"
    if not export_path.is_file():
        return

    digest_before = compute_sha256_digest(export_path)

    raw_bytes = export_path.read_bytes()
    html_document = BeautifulSoup(raw_bytes, "lxml")
    table_rows = html_document.find_all("tr")
    assert len(table_rows) > 0, (
        "Le fichier `ExportIndividus.xls` doit contenir des lignes de tableau HTML analysables."
    )

    digest_after = compute_sha256_digest(export_path)
    assert digest_before == digest_after, (
        "L'intégrité du fichier `ExportIndividus.xls` ne doit jamais être modifiée."
    )


def test_pyproject_toml_and_cli_entrypoints() -> None:
    """Vérifie que `pyproject.toml` déclare `sgdf-contacts` et ses 3 exécutables CLI."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "Le fichier `pyproject.toml` doit exister à la racine."

    pyproject_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project_section = pyproject_data.get("project", {})
    assert project_section.get("name") == "sgdf-contacts"

    scripts = project_section.get("scripts", {})
    assert scripts.get("sgdf-extract") == "sgdf_contacts.entrypoints.cli_extract:main"
    assert scripts.get("sgdf-vcf") == "sgdf_contacts.entrypoints.cli_vcf:main"
    assert scripts.get("sgdf-api") == "sgdf_contacts.entrypoints.api:run_server"

    from sgdf_contacts.entrypoints import run_extract_cli, run_server, run_vcf_cli

    assert callable(run_extract_cli)
    assert callable(run_vcf_cli)
    assert callable(run_server)


def test_flake_packaging_and_nixos_module_declaration() -> None:
    """Vérifie que `flake.nix` expose `buildPythonApplication`, `oci-image`, `apps.sgdf-api` et `nixosModules.default`."""
    flake_path = PROJECT_ROOT / "flake.nix"
    flake_content = flake_path.read_text(encoding="utf-8")

    for required_token in (
        "buildPythonApplication",
        "dockerTools.buildLayeredImage",
        "oci-image",
        "sgdf-api",
        "sgdf-extract",
        "sgdf-vcf",
        "nixosModules",
        "services.sgdf-utils",
        "environmentFile",
        "DynamicUser = true",
        'StateDirectory = "sgdf-utils"',
        'ProtectSystem = "strict"',
        "ProtectHome = true",
        "PrivateTmp = true",
        "NoNewPrivileges = true",
    ):
        assert required_token in flake_content, (
            f"L'élément '{required_token}' doit être déclaré dans `flake.nix`."
        )
