# Data Model & Configuration Schema: Empaquetage Nix et Module NixOS (`services.sgdf-utils`)

**Feature**: `010-packager-flake-module-nixos` | **Date**: 2026-10-27

Cette fonctionnalité n'introduit pas de nouvelles tables SQLite mais formalise trois contrats de configuration et de distribution :

## 1. Métadonnées et Scripts du Paquet Python (`pyproject.toml`)

| Champ / Section | Valeur | Description |
|-----------------|--------|-------------|
| `project.name` | `"sgdf-contacts"` | Nom normalisé de la distribution Python |
| `project.version` | `"1.0.0"` | Version sémantique alignée sur l'API FastAPI |
| `project.requires-python` | `">=3.10"` | Version minimale de Python 3 supportée |
| `project.scripts.sgdf-extract` | `"sgdf_contacts.entrypoints.cli_extract:main"` | Commande CLI d'extraction `ExportIndividus.xls` -> `ContactsParents.xlsx` |
| `project.scripts.sgdf-vcf` | `"sgdf_contacts.entrypoints.cli_vcf:main"` | Commande CLI de génération `ContactsParents.xlsx` -> `ContactParents.vcf` |
| `project.scripts.sgdf-api` | `"sgdf_contacts.entrypoints.api:run_server"` | Commande de lancement du serveur FastAPI/Uvicorn |

---

## 2. Options du Module NixOS (`services.sgdf-utils`)

| Option | Type Nix | Valeur par défaut | Description |
|--------|----------|-------------------|-------------|
| `services.sgdf-utils.enable` | `lib.types.bool` | `false` | Active le service HTTP REST `sgdf-utils` |
| `services.sgdf-utils.package` | `lib.types.package` | `self.packages.${pkgs.stdenv.hostPlatform.system}.default` | Paquet fournissant l'exécutable `sgdf-api` |
| `services.sgdf-utils.host` | `lib.types.str` | `"127.0.0.1"` | Adresse IP d'écoute (`SGDF_HOST`) |
| `services.sgdf-utils.port` | `lib.types.port` | `8000` | Port TCP d'écoute (`SGDF_PORT`) |
| `services.sgdf-utils.dataDir` | `lib.types.str` | `"/var/lib/sgdf-utils"` | Répertoire de stockage persistant de `sgdf.sqlite3` |
| `services.sgdf-utils.environmentFile` | `lib.types.nullOr lib.types.path` | `null` | Fichier de secrets (`sops-nix` / `agenix`) contenant `SGDF_API_KEY` |

---

## 3. Correspondance vers l'Unité `systemd.services.sgdf-utils`

Lorsque `services.sgdf-utils.enable = true` :

| Paramètre `systemd` | Valeur générée | Rôle |
|---------------------|----------------|------|
| `environment.SGDF_HOST` | `cfg.host` (défaut `"127.0.0.1"`) | Adresse d'écoute transmise à `ApiSettings` |
| `environment.SGDF_PORT` | `toString cfg.port` (défaut `"8000"`) | Port d'écoute transmis à `ApiSettings` |
| `environment.SGDF_DATABASE_URL` | `"sqlite:///${cfg.dataDir}/sgdf.sqlite3"` | URL SQLAlchemy SQLite avec 4 barres obliques pour chemin absolu (`/var/lib/sgdf-utils/sgdf.sqlite3`) |
| `serviceConfig.ExecStart` | `"${cfg.package}/bin/sgdf-api"` | Exécutable principal du service |
| `serviceConfig.EnvironmentFile` | `cfg.environmentFile` *(si non nul)* | Injection sécurisée de `SGDF_API_KEY` hors du `/nix/store` |
| `serviceConfig.DynamicUser` | `true` | Utilisateur système éphémère dédié sans privilèges |
| `serviceConfig.StateDirectory` | `"sgdf-utils"` | Création et persistance automatiques de `/var/lib/sgdf-utils` |
| `serviceConfig.WorkingDirectory` | `cfg.dataDir` | Répertoire de travail du processus |
| `serviceConfig.ProtectSystem` | `"strict"` | Montage en lecture seule de l'arborescence système |
| `serviceConfig.ProtectHome` | `true` | Inaccessibilité totale de `/home`, `/root` et `/run/user` |
| `serviceConfig.PrivateTmp` | `true` | Espace `/tmp` et `/var/tmp` privé et isolé |
| `serviceConfig.NoNewPrivileges` | `true` | Interdiction d'élévation de privilèges (`setuid`/`setgid`) |
