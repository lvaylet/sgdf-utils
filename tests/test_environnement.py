"""Tests automatisés de l'environnement de développement éphémère SGDF La Rochelle.

Ce module vérifie :
1. La présence et l'isolation de l'interpréteur Python 3 et des outils requis.
2. L'importation sans erreur de toutes les bibliothèques Python nécessaires aux scripts SGDF.
3. La parité stricte entre les définitions déclaratives `flake.nix` et `devbox.json`.
4. Le fonctionnement de la matrice de décision `.envrc` selon `OUTIL_ENVIRONNEMENT`.
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
from pathlib import Path

from bs4 import BeautifulSoup

RACINE_PROJET = Path(__file__).resolve().parent.parent

MODULES_PYTHON_REQUIS = (
    "pandas",
    "bs4",
    "lxml",
    "xlrd",
    "openpyxl",
    "pytest",
)

PAQUETS_NIX_ATTENDUS = (
    "pandas",
    "beautifulsoup4",
    "lxml",
    "xlrd",
    "openpyxl",
    "pytest",
    "ruff",
)


def calculer_empreinte_sha256(chemin_fichier: Path) -> str:
    """Calcule l'empreinte SHA-256 d'un fichier sans le modifier."""
    hacheur = hashlib.sha256()
    with chemin_fichier.open("rb") as flux_lecture:
        for bloc in iter(lambda: flux_lecture.read(65536), b""):
            hacheur.update(bloc)
    return hacheur.hexdigest()


def test_version_et_isolation_python() -> None:
    """Vérifie que Python 3 est actif et provient d'un environnement isolé (Nix ou Devbox)."""
    assert sys.version_info >= (3, 10), "Python 3.10 ou supérieur est requis."

    chemin_executable = Path(sys.executable).resolve()
    texte_chemin = str(chemin_executable)
    est_isole = ("/nix/store/" in texte_chemin) or (".devbox" in texte_chemin)
    assert est_isole, (
        f"L'interpréteur Python ({texte_chemin}) doit provenir du store Nix ou de Devbox."
    )


def test_importation_bibliotheques_sgdf() -> None:
    """Vérifie que toutes les bibliothèques requises pour les scripts SGDF sont importables."""
    for nom_module in MODULES_PYTHON_REQUIS:
        module_importe = importlib.import_module(nom_module)
        assert module_importe is not None, f"Échec de l'importation du module {nom_module}."


def test_disponibilite_outils_cli() -> None:
    """Vérifie que les exécutables `pytest` et `ruff` sont disponibles dans le PATH."""
    for outil in ("python3", "pytest", "ruff"):
        chemin_outil = shutil.which(outil)
        assert chemin_outil is not None, f"L'outil '{outil}' doit être disponible dans le PATH."


def test_conformite_flake_nix_et_verrouillage() -> None:
    """Vérifie que `flake.nix` et `flake.lock` existent et déclarent tous les paquets en français."""
    chemin_flake = RACINE_PROJET / "flake.nix"
    chemin_verrou = RACINE_PROJET / "flake.lock"

    assert chemin_flake.is_file(), "Le fichier `flake.nix` doit exister à la racine."
    assert chemin_verrou.is_file(), "Le fichier `flake.lock` doit exister à la racine."

    contenu_flake = chemin_flake.read_text(encoding="utf-8")
    assert "python3.withPackages" in contenu_flake, (
        "`flake.nix` doit utiliser `python3.withPackages` sans pip ni .venv."
    )
    for paquet in PAQUETS_NIX_ATTENDUS:
        assert paquet in contenu_flake, f"Le paquet '{paquet}' doit figurer dans `flake.nix`."

    assert "SGDF" in contenu_flake and "Environnement" in contenu_flake, (
        "`flake.nix` doit contenir une description et un message d'accueil en français."
    )


def test_conformite_et_parite_devbox_json() -> None:
    """Vérifie que `devbox.json` est valide et en parité stricte à 100 % avec `flake.nix`."""
    chemin_devbox = RACINE_PROJET / "devbox.json"
    assert chemin_devbox.is_file(), "Le fichier `devbox.json` doit exister à la racine."

    donnees_devbox = json.loads(chemin_devbox.read_text(encoding="utf-8"))
    paquets_devbox = donnees_devbox.get("packages", [])
    texte_paquets = " ".join(paquets_devbox)

    assert any(p.startswith("python3") for p in paquets_devbox), (
        "`devbox.json` doit déclarer l'interpréteur `python3`."
    )
    for paquet in PAQUETS_NIX_ATTENDUS:
        assert paquet in texte_paquets, (
            f"Le paquet '{paquet}' doit être présent dans `devbox.json` pour assurer la parité."
        )

    configuration_shell = donnees_devbox.get("shell", {})
    commandes_accueil = "\n".join(configuration_shell.get("init_hook", []))
    assert "Environnement" in commandes_accueil, (
        "Le message d'accueil `init_hook` de `devbox.json` doit être rédigé en français."
    )

    scripts_devbox = configuration_shell.get("scripts", {})
    for nom_script in ("verifier_environnement", "tester", "verifier_qualite"):
        assert nom_script in scripts_devbox, (
            f"Le script en français '{nom_script}' doit être défini dans `devbox.json`."
        )


def test_matrice_decision_envrc(tmp_path: Path) -> None:
    """Vérifie la logique de sélection `.envrc` selon `OUTIL_ENVIRONNEMENT` et les outils présents."""
    chemin_envrc = RACINE_PROJET / ".envrc"
    assert chemin_envrc.is_file(), "Le fichier `.envrc` doit exister à la racine."

    contenu_envrc = chemin_envrc.read_text(encoding="utf-8")
    assert "OUTIL_ENVIRONNEMENT" in contenu_envrc
    assert "use flake" in contenu_envrc
    assert "devbox generate direnv" in contenu_envrc

    script_harnais = tmp_path / "harnais_envrc.sh"
    script_harnais.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
source_env_if_exists() { :; }
watch_file() { :; }
has() {
    local outil="$1"
    if [[ "$outil" == "nix" && "${SIMULER_NIX:-0}" == "1" ]]; then return 0; fi
    if [[ "$outil" == "devbox" && "${SIMULER_DEVBOX:-0}" == "1" ]]; then return 0; fi
    return 1
}
use() {
    echo "ACTION_ACTIVE=flake:$*"
}
devbox() {
    if [[ "$1" == "generate" && "$2" == "direnv" ]]; then
        echo "echo ACTION_ACTIVE=devbox"
    fi
}
source "$CHEMIN_ENVRC"
""",
        encoding="utf-8",
    )

    def executer_scenario(
        outil_env: str | None,
        simuler_nix: bool,
        simuler_devbox: bool,
    ) -> subprocess.CompletedProcess[str]:
        env_test = os.environ.copy()
        env_test["CHEMIN_ENVRC"] = str(chemin_envrc)
        env_test["SIMULER_NIX"] = "1" if simuler_nix else "0"
        env_test["SIMULER_DEVBOX"] = "1" if simuler_devbox else "0"
        if outil_env is None:
            env_test.pop("OUTIL_ENVIRONNEMENT", None)
        else:
            env_test["OUTIL_ENVIRONNEMENT"] = outil_env

        return subprocess.run(
            ["bash", str(script_harnais)],
            env=env_test,
            capture_output=True,
            text=True,
            check=False,
        )

    # 1. Mode par défaut (auto) avec Nix et Devbox présents -> Priorité à flake.nix
    res_auto_deux = executer_scenario(None, simuler_nix=True, simuler_devbox=True)
    assert res_auto_deux.returncode == 0
    assert "ACTION_ACTIVE=flake:flake" in res_auto_deux.stdout
    assert "ACTION_ACTIVE=devbox" not in res_auto_deux.stdout

    # 2. Mode par défaut (auto) avec uniquement Devbox présent -> Repli sur devbox.json
    res_auto_devbox = executer_scenario(None, simuler_nix=False, simuler_devbox=True)
    assert res_auto_devbox.returncode == 0
    assert "ACTION_ACTIVE=devbox" in res_auto_devbox.stdout

    # 3. Bascule explicite vers devbox quand les deux sont présents
    res_force_devbox = executer_scenario("devbox", simuler_nix=True, simuler_devbox=True)
    assert res_force_devbox.returncode == 0
    assert "ACTION_ACTIVE=devbox" in res_force_devbox.stdout
    assert "ACTION_ACTIVE=flake:flake" not in res_force_devbox.stdout

    # 4. Bascule explicite vers flake quand les deux sont présents
    res_force_flake = executer_scenario("flake", simuler_nix=True, simuler_devbox=True)
    assert res_force_flake.returncode == 0
    assert "ACTION_ACTIVE=flake:flake" in res_force_flake.stdout

    # 5. Absence simultanée de Nix et Devbox -> Message d'erreur en français sans planter le shell
    res_aucun_outil = executer_scenario("auto", simuler_nix=False, simuler_devbox=False)
    sortie_combinee = res_aucun_outil.stdout + res_aucun_outil.stderr
    assert "Erreur" in sortie_combinee or "aucun" in sortie_combinee.lower()

    # 6. Valeur invalide de OUTIL_ENVIRONNEMENT -> Message d'erreur en français
    res_invalide = executer_scenario("inconnu", simuler_nix=True, simuler_devbox=True)
    sortie_invalide = res_invalide.stdout + res_invalide.stderr
    assert "OUTIL_ENVIRONNEMENT" in sortie_invalide


def test_protection_donnees_gitignore() -> None:
    """Vérifie que `.gitignore` protège les fichiers d'export SGDF et les caches locaux."""
    chemin_gitignore = RACINE_PROJET / ".gitignore"
    assert chemin_gitignore.is_file(), "Le fichier `.gitignore` doit exister à la racine."

    contenu_gitignore = chemin_gitignore.read_text(encoding="utf-8")
    for motif_requis in (
        "*.xls",
        "*.xlsx",
        "*.csv",
        "ExportIndividus*",
        ".direnv/",
        ".devbox/",
        ".envrc.local",
    ):
        assert motif_requis in contenu_gitignore, (
            f"Le motif '{motif_requis}' doit figurer dans `.gitignore`."
        )


def test_lecture_seule_export_individus() -> None:
    """Vérifie que `ExportIndividus.xls` peut être analysé en lecture seule sans altération."""
    chemin_export = RACINE_PROJET / "ExportIndividus.xls"
    if not chemin_export.is_file():
        return

    empreinte_avant = calculer_empreinte_sha256(chemin_export)

    contenu_brut = chemin_export.read_bytes()
    document_html = BeautifulSoup(contenu_brut, "lxml")
    lignes_tableau = document_html.find_all("tr")
    assert len(lignes_tableau) > 0, (
        "Le fichier `ExportIndividus.xls` doit contenir des lignes de tableau HTML analysables."
    )

    empreinte_apres = calculer_empreinte_sha256(chemin_export)
    assert empreinte_avant == empreinte_apres, (
        "L'intégrité du fichier `ExportIndividus.xls` ne doit jamais être modifiée."
    )
