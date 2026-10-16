# Modèle de Données et d'Entités de Configuration : Environnement Éphémère

**Branche** : `001-env-dev-ephemere` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

Cette fonctionnalité porte sur l'infrastructure d'environnement de développement déclaratif. Elle ne manipule pas de base de données métier, mais structure trois entités de configuration interdépendantes garantissant la parité et l'isolation de l'environnement.

## 1. Entités de Configuration

### 1.1. Définition Nix Flake (`flake.nix` & `flake.lock`)

- **Rôle** : Source de vérité déclarative pour l'option Nix Flakes (option prioritaire par défaut).
- **Attributs clés** :
  - `description` : Description en français de l'environnement d'automatisation SGDF La Rochelle.
  - `inputs.nixpkgs` : Référence vers le canal Nixpkgs fournissant Python 3 et ses paquets.
  - `outputs.devShells.<system>.default` : Coquille de développement exposant :
    - L'interpréteur Python 3 pré-configuré avec `pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`.
    - L'outil d'analyse et de formatage `ruff`.
    - `shellHook` : Script d'accueil affichant en français la confirmation d'activation de l'environnement Nix Flake et la version de Python active.
- **Règles de validation** :
  - DOIT passer `nix flake check` ou `nix develop --command python3 -c "..."` sans erreur.
  - Tous les commentaires et messages `shellHook` DOIVENT être en français.

### 1.2. Définition Jetify Devbox (`devbox.json`)

- **Rôle** : Source de vérité déclarative pour l'option Jetify Devbox (option parallèle et de repli).
- **Attributs clés** :
  - `packages` : Liste des paquets Nixpkgs (`python3`, `python3Packages.pandas`, `python3Packages.beautifulsoup4`, `python3Packages.lxml`, `python3Packages.xlrd`, `python3Packages.openpyxl`, `python3Packages.pytest`, `ruff`).
  - `shell.init_hook` : Message d'accueil en français confirmant l'activation de l'environnement Devbox et la version de Python active.
  - `shell.scripts` : Commandes raccourcies nommées en français (`verifier_environnement`, `tester`, `verifier_qualite`) pour faciliter le travail des bénévoles.
- **Règles de validation** :
  - DOIT être un document JSON valide conforme au schéma Jetify Devbox.
  - DOIT fournir exactement le même ensemble de bibliothèques Python et d'outils que `flake.nix`.

### 1.3. Orchestrateur d'Activation (`.envrc`)

- **Rôle** : Script évalué automatiquement par `direnv` à l'entrée dans le répertoire du projet.
- **Paramètres d'entrée** :
  - `.envrc.local` (optionnel, non versionné) : Surcharge locale éventuelle pour le poste du bénévole.
  - `OUTIL_ENVIRONNEMENT` (variable d'environnement, valeurs : `auto` | `flake` | `devbox`, défaut : `auto`).
- **Règles de transition d'état** :
  1. **État initial (Hors du dossier)** : Environnement système hôte standard.
  2. **Entrée dans le dossier (`cd contacts-parents`)** :
     - Si `OUTIL_ENVIRONNEMENT="flake"` → Vérifie `nix` → Active `flake.nix` (`use flake`).
     - Si `OUTIL_ENVIRONNEMENT="devbox"` → Vérifie `devbox` → Active `devbox.json`.
     - Si `OUTIL_ENVIRONNEMENT="auto"` :
       - Si `nix` est présent → Active `flake.nix` (`use flake`).
       - Sinon, si `devbox` est présent → Active `devbox.json`.
       - Sinon → Affiche une erreur en français sur la sortie d'erreur sans faire planter le shell.
  3. **Sortie du dossier (`cd ..`)** : `direnv` restaure intégralement les variables d'environnement initiales du système hôte.

### 1.4. Règles d'Exclusion et de Protection (`.gitignore`)

- **Rôle** : Garde-fou de confidentialité (RGPD) et de propreté technique.
- **Catégories exclues** :
  - Caches d'environnement éphémère : `.direnv/`, `.devbox/`, `.envrc.local`.
  - Caches Python et outils : `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`.
  - Fichiers de données personnelles SGDF : `*.xls`, `*.xlsx`, `*.csv`, `ExportIndividus*`.

## 2. Relations entre Entités

```text
[Entrée dans le dossier]
          │
          ▼
       .envrc  ◄── (optionnel) .envrc.local / OUTIL_ENVIRONNEMENT
          │
    ┌─────┴──────────────────────┐
    │ Priorité 1 (ou "flake")    │ Repli (ou "devbox")
    ▼                            ▼
flake.nix (+ flake.lock)     devbox.json (+ devbox.lock)
    │                            │
    └─────────────┬──────────────┘
                  ▼
  [Environnement Python 3 Éphémère Unifié]
  (python3, pandas, bs4, lxml, xlrd, openpyxl, pytest, ruff)
```
