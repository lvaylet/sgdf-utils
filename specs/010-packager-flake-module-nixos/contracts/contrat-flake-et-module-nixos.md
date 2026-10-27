# Contrat d'Interface : Sorties `flake.nix`, Exécutables CLI et Module NixOS

**Feature**: `010-packager-flake-module-nixos` | **Date**: 2026-10-27

## 1. Sorties du Flake Nix (`flake.nix`)

| Sortie Flake | Plateformes | Type | Description |
|--------------|-------------|------|-------------|
| `packages.<system>.default` | Linux & Darwin (`x86_64`, `aarch64`) | Dérivation (`buildPythonApplication`) | Paquet Python `sgdf-contacts` contenant `sgdf-extract`, `sgdf-vcf` et `sgdf-api`, vérifié par `pytest` dans `checkPhase` |
| `packages.<system>.sgdf-contacts` | Linux & Darwin (`x86_64`, `aarch64`) | Dérivation (`buildPythonApplication`) | Alias explicite de `packages.<system>.default` |
| `packages.<system>.oci-image` | Linux (`x86_64-linux`, `aarch64-linux`) | Archive OCI (`dockerTools.buildLayeredImage`) | Image conteneur minimale lançant `sgdf-api` sur le port `8000` avec volume `/data` |
| `apps.<system>.default` | Linux & Darwin | Application Nix (`type = "app"`) | Lance `${packages.<system>.default}/bin/sgdf-api` |
| `apps.<system>.sgdf-api` | Linux & Darwin | Application Nix (`type = "app"`) | Permet `nix run .#sgdf-api` |
| `apps.<system>.sgdf-extract` | Linux & Darwin | Application Nix (`type = "app"`) | Permet `nix run .#sgdf-extract -- --help` |
| `apps.<system>.sgdf-vcf` | Linux & Darwin | Application Nix (`type = "app"`) | Permet `nix run .#sgdf-vcf -- --help` |
| `devShells.<system>.default` | Linux & Darwin | Shell de développement (`mkShell`) | Environnement éphémère de développement activé par `direnv` |
| `nixosModules.default` | NixOS | Module NixOS | Déclare les options `services.sgdf-utils` et configure `systemd.services.sgdf-utils` |
| `nixosModules.sgdf-utils` | NixOS | Module NixOS | Alias explicite de `nixosModules.default` |
| `checks.<system>.package` | Linux & Darwin | Dérivation de vérification | Valide la construction du paquet et l'exécution de `pytest` |
| `checks.<system>.nixos-module` | Linux (`x86_64-linux`, `aarch64-linux`) | Dérivation de vérification | Évalue une configuration NixOS de test avec `nixosModules.default` et vérifie les options et le durcissement `systemd` |

---

## 2. Contrat des Exécutables CLI (`[project.scripts]`)

### `sgdf-extract`

```bash
sgdf-extract [--input ExportIndividus.xls] [--output ContactsParents.xlsx]
```

- Code de retour `0` en cas de succès, `1` en cas d'erreur d'entrée/sortie ou de format.
- Messages d'aide (`--help`), de succès et d'erreur en français.

### `sgdf-vcf`

```bash
sgdf-vcf [--input ContactsParents.xlsx] [--output ContactParents.vcf]
```

- Code de retour `0` en cas de succès, `1` en cas d'erreur.
- Messages d'aide (`--help`), de succès et d'erreur en français.

### `sgdf-api`

```bash
SGDF_HOST=127.0.0.1 SGDF_PORT=8000 SGDF_DATABASE_URL=sqlite:///sgdf_contacts.db sgdf-api
```

- Démarre le serveur ASGI Uvicorn exposant `sgdf_contacts.entrypoints.api:app`.

---

## 3. Contrat d'Utilisation du Module NixOS (`nixosModules.default`)

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    sgdf-utils.url = "github:lvaylet/sgdf-utils";
  };

  outputs = { self, nixpkgs, sgdf-utils, ... }: {
    nixosConfigurations.homelab = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        sgdf-utils.nixosModules.default
        ({ config, ... }: {
          services.sgdf-utils = {
            enable = true;
            host = "127.0.0.1";
            port = 8000;
            dataDir = "/var/lib/sgdf-utils";
            environmentFile = config.sops.secrets."sgdf-utils/env".path;
          };
        })
      ];
    };
  };
}
```
