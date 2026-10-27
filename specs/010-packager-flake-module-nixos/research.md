# Research: Empaquetage Nix (`pyproject.toml`, `buildPythonApplication`, `oci-image`) et Module NixOS (`nixosModules.default`)

**Feature**: `010-packager-flake-module-nixos` | **Date**: 2026-10-27

## Decision 1: Packaging Python standard via `pyproject.toml` et points d'entrée `sgdf_contacts/entrypoints/`

- **Decision**: Créer un fichier `pyproject.toml` standard (PEP 621) utilisant `setuptools.build_meta` et déclarant le paquet `sgdf-contacts` ainsi que trois scripts dans `[project.scripts]` :
  - `sgdf-extract = "sgdf_contacts.entrypoints.cli_extract:main"`
  - `sgdf-vcf = "sgdf_contacts.entrypoints.cli_vcf:main"`
  - `sgdf-api = "sgdf_contacts.entrypoints.api:run_server"`
  Déplacer l'implémentation CLI de `extract_parent_contacts.py` et `generate_contacts_vcf.py` dans `sgdf_contacts/entrypoints/cli_extract.py` et `sgdf_contacts/entrypoints/cli_vcf.py`, tout en conservant `extract_parent_contacts.py` et `generate_contacts_vcf.py` à la racine du dépôt comme façades rétrocompatibles ré-exportant exactement les mêmes symboles (et incluses via `py-modules` dans `pyproject.toml`).
- **Rationale**:
  - Lorsqu'une roue Python (`wheel`) est construite et installée par `buildPythonApplication`, les wrappers générés dans `$out/bin/` importent les modules installés dans `site-packages`. Loger les trois points d'entrée dans `sgdf_contacts.entrypoints` garantit une architecture homogène (`cli_extract.py`, `cli_vcf.py`, `api.py`).
  - Conserver `extract_parent_contacts.py` et `generate_contacts_vcf.py` à la racine avec ré-export intégral préserve à 100 % la compatibilité avec les habitudes des bénévoles (`python3 extract_parent_contacts.py`) et avec tous les tests existants (`test_extract_parent_contacts.py`, `test_generate_contacts_vcf.py`, `test_sgdf_contacts_package.py`).
  - En Python, un point d'entrée `[project.scripts]` appelle `sys.exit(func())` : une fonction `main() -> int` retournant `0` en cas de succès et `1` en cas d'erreur se comporte donc nativement comme attendu en ligne de commande.
- **Alternatives considered**:
  - *Pointer `[project.scripts]` uniquement vers les fichiers à la racine sans sous-modules `entrypoints/`* : Moins cohérent avec `sgdf_contacts/entrypoints/api.py` introduit à l'étape 3.

## Decision 2: Construction Nix reproductible avec `buildPythonApplication` et `pytestCheckHook`

- **Decision**: Dans `flake.nix`, définir `packages.<system>.default` (et l'alias `packages.<system>.sgdf-contacts`) via `pkgs.python3Packages.buildPythonApplication` avec :
  - `pname = "sgdf-contacts";`
  - `version = "1.0.0";`
  - `pyproject = true;`
  - `build-system = [ pkgs.python3Packages.setuptools ];`
  - `dependencies = with pkgs.python3Packages; [ pandas beautifulsoup4 lxml xlrd openpyxl sqlmodel sqlalchemy fastapi uvicorn python-multipart httpx ];`
  - `nativeCheckInputs = [ pkgs.python3Packages.pytestCheckHook pkgs.ruff ];`
- **Rationale**:
  - `pytestCheckHook` exécute automatiquement `pytest` pendant la `checkPhase` dans le bac à sable isolé de Nix lors de `nix build` et `nix flake check`.
  - Inclure `pkgs.ruff` dans `nativeCheckInputs` permet au test existant `test_cli_tools_availability` (`tests/test_environment.py`), qui vérifie la présence de `python3`, `pytest` et `ruff` dans le `PATH`, de réussir également à l'intérieur du bac à sable Nix.
  - Les tests qui accèdent à `ExportIndividus.xls` ou `ContactsParents.xlsx` (fichiers ignorés par Git pour conformité RGPD) vérifient déjà `if not export_path.is_file(): return` et s'exécutent donc proprement dans le bac à sable Nix pendant que tous les tests synthétiques s'exécutent intégralement.
- **Alternatives considered**:
  - *Désactiver `doCheck`* : Contraire au critère d'acceptation de l'issue #6 (*"`nix build` construit le paquet Python et exécute la suite de tests `pytest` dans le bac à sable Nix"*).

## Decision 3: Applications Nix (`apps`) pour `nix run .#sgdf-api`

- **Decision**: Déclarer la sortie `apps` dans `flake.nix` pour chaque système supporté :
  - `apps.<system>.default` pointant vers `${sgdfPackage}/bin/sgdf-api`,
  - `apps.<system>.sgdf-api` pointant vers `${sgdfPackage}/bin/sgdf-api`,
  - `apps.<system>.sgdf-extract` pointant vers `${sgdfPackage}/bin/sgdf-extract`,
  - `apps.<system>.sgdf-vcf` pointant vers `${sgdfPackage}/bin/sgdf-vcf`.
- **Rationale**:
  - Répond directement au critère d'acceptation `nix run .#sgdf-api` tout en permettant aussi `nix run .#sgdf-extract` et `nix run .#sgdf-vcf`.
- **Alternatives considered**:
  - *Compter uniquement sur `packages.sgdf-api` avec `meta.mainProgram`* : Déclarer explicitement `apps.<system>.sgdf-api` fonctionne sans ambiguïté quelle que soit la version de Nix et permet d'exposer les 3 binaires issus du même paquet `sgdf-contacts` sans reconstruire 3 fois la dérivation.

## Decision 4: Image conteneur OCI minimale (`packages.oci-image`)

- **Decision**: Sur les plateformes Linux (`pkgs.stdenv.isLinux`), exposer `packages.<system>.oci-image` construit avec `pkgs.dockerTools.buildLayeredImage` :
  - `name = "sgdf-utils";`
  - `tag = "latest";`
  - `contents = [ sgdfPackage pkgs.cacert ];`
  - `config = { Cmd = [ "${sgdfPackage}/bin/sgdf-api" ]; Env = [ "SGDF_HOST=0.0.0.0" "SGDF_PORT=8000" "SGDF_DATABASE_URL=sqlite:////data/sgdf.sqlite3" ]; ExposedPorts = { "8000/tcp" = {}; }; Volumes = { "/data" = {}; }; WorkingDir = "/data"; };`
- **Rationale**:
  - `dockerTools.buildLayeredImage` ne construit des images Linux que sur un hôte Linux ; le conditionner à `pkgs.stdenv.isLinux` préserve la compatibilité Darwin du reste du flake tout en fournissant `packages.x86_64-linux.oci-image` et `packages.aarch64-linux.oci-image` pour le homelab Podman/Docker.
- **Alternatives considered**:
  - *Construire un `Dockerfile` classique avec `pip`* : Non reproductible et contraire à l'approche déclarative Nix demandée dans l'issue #6.

## Decision 5: Module NixOS déclaratif (`nixosModules.default`) et durcissement `systemd`

- **Decision**: Exposer `nixosModules.default` (et l'alias `nixosModules.sgdf-utils`) dans `flake.nix`, déclarant `options.services.sgdf-utils` (`enable`, `package`, `host`, `port`, `dataDir`, `environmentFile`) et générant `systemd.services.sgdf-utils` avec :
  - Variables d'environnement : `SGDF_HOST = cfg.host`, `SGDF_PORT = toString cfg.port`, `SGDF_DATABASE_URL = "sqlite:///${cfg.dataDir}/sgdf.sqlite3"`.
  - Durcissement `serviceConfig` :
    - `ExecStart = "${cfg.package}/bin/sgdf-api";`
    - `WorkingDirectory = cfg.dataDir;`
    - `DynamicUser = true;`
    - `StateDirectory = "sgdf-utils";`
    - `ProtectSystem = "strict";`
    - `ProtectHome = true;`
    - `PrivateTmp = true;`
    - `NoNewPrivileges = true;`
    - `EnvironmentFile = cfg.environmentFile;` (uniquement si `cfg.environmentFile != null`)
    - `ReadWritePaths = [ cfg.dataDir ];` (ajouté si `cfg.dataDir != "/var/lib/sgdf-utils"`)
- **Rationale**:
  - Avec `DynamicUser = true` et `StateDirectory = "sgdf-utils"`, `systemd` crée automatiquement `/var/lib/sgdf-utils` avec les permissions exclusives de l'utilisateur dynamique et le conserve entre les redémarrages, malgré `ProtectSystem = "strict"`.
  - L'utilisation de `EnvironmentFile` garantit que `SGDF_API_KEY` (fourni par `sops-nix` ou `agenix`) est lu à l'exécution par `systemd` et n'est jamais copié en clair dans `/nix/store`.
  - Pour valider automatiquement le module lors de `nix flake check` sans exiger KVM, ajouter un check `checks.<system>.nixos-module` qui évalue une configuration NixOS minimale (`nixpkgs.lib.nixosSystem`) activant `services.sgdf-utils` et vérifie par assertions Nix l'ensemble des attributs de `config.systemd.services.sgdf-utils`.
- **Alternatives considered**:
  - *Passer `SGDF_API_KEY` directement en option Nix `types.str`* : Dangereux car toute chaîne Nix est écrite en clair dans `/nix/store` lisible par tous les utilisateurs locaux ; `environmentFile` est la bonne pratique standard NixOS.
