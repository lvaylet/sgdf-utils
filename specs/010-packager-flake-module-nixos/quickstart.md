# Quickstart Validation Guide: Empaquetage Nix et Module NixOS (`sgdf-utils`)

**Feature**: `010-packager-flake-module-nixos` | **Date**: 2026-10-27

## Prérequis

- `nix` avec `nix-command` et `flakes` activés
- `direnv` (`direnv allow` à la racine du dépôt)

## 1. Vérifier la suite de tests et le style du code dans l'environnement de développement

```bash
pytest -v
ruff check .
```

**Résultat attendu** : 100 % des tests unitaires, d'intégration et de packaging passent, et `ruff check .` ne signale aucune erreur.

## 2. Construire le paquet Python via Nix (`nix build`)

```bash
nix build
./result/bin/sgdf-extract --help
./result/bin/sgdf-vcf --help
```

**Résultat attendu** :
- `nix build` construit la dérivation `sgdf-contacts` et exécute `pytest` dans la `checkPhase` du bac à sable Nix.
- `./result/bin/sgdf-extract`, `./result/bin/sgdf-vcf` et `./result/bin/sgdf-api` sont présents et exécutables.

## 3. Tester le lancement direct du serveur API (`nix run .#sgdf-api`)

```bash
SGDF_PORT=18080 SGDF_DATABASE_URL="sqlite:////tmp/opencode/sgdf-quickstart.db" nix run .#sgdf-api &
API_PID=$!
sleep 2
curl -s http://127.0.0.1:18080/health
kill "$API_PID"
```

**Résultat attendu** : `GET /health` retourne `{"status":"ok","database":"ok"}`.

## 4. Construire l'image conteneur OCI (`nix build .#oci-image`)

```bash
nix build .#oci-image
ls -lh ./result
```

**Résultat attendu** : `./result` pointe vers l'archive `.tar.gz` de l'image OCI en couches prête pour `podman load < ./result` ou `docker load < ./result`.

## 5. Valider l'intégralité du Flake et du module NixOS (`nix flake check`)

```bash
nix flake check
```

**Résultat attendu** : `nix flake check` valide les sorties `packages`, `apps`, `devShells`, `nixosModules.default` et `checks` (incluant l'évaluation complète du service `systemd.services.sgdf-utils` et de son durcissement).
