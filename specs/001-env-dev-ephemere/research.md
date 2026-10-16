# Recherche Technique : Environnement de Développement Éphémère Double Option (`flake.nix` et `devbox.json`)

**Branche** : `001-env-dev-ephemere` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

## 1. Fourniture déclarative de Python 3 et de ses bibliothèques dans `flake.nix`

- **Decision** : Utiliser `pkgs.python3.withPackages (ps: with ps; [ pandas beautifulsoup4 lxml xlrd openpyxl pytest ])` associé à `pkgs.ruff` au sein du `devShells.default` dans `flake.nix`, en ciblant `nixpkgs` (`nixos-unstable` / `nixpkgs-unstable`) pour les systèmes `x86_64-linux`, `aarch64-linux`, `x86_64-darwin` et `aarch64-darwin`.
- **Rationale** : `python3.withPackages` génère une dérivation Nix unique contenant l'interpréteur Python 3 et toutes les bibliothèques pré-liées dans le store Nix. Dès l'activation par `direnv` (`use flake`), toutes les bibliothèques sont immédiatement importables sans exécuter `pip install` ni gérer de dossier `.venv`, répondant exactement aux exigences `FR-002` et `SC-001`.
- **Alternatives considered** :
  - *`venvShellHook` avec `pip install -r requirements.txt`* : Rejeté suite à la clarification `FR-002`, car cela impose une étape d'installation réseau mutable dans un dossier `.venv` et ralentit l'initialisation.
  - *Gestionnaire `poetry` ou `uv` externe* : Rejeté car introduit un second fichier de verrouillage Python redondant avec `flake.lock` et `devbox.lock` (contraire au Principe V de simplicité YAGNI).

## 2. Parité déclarative dans `devbox.json`

- **Decision** : Déclarer dans `devbox.json` la liste de paquets Nix équivalente : `python3@latest`, `python3Packages.pandas@latest`, `python3Packages.beautifulsoup4@latest`, `python3Packages.lxml@latest`, `python3Packages.xlrd@latest`, `python3Packages.openpyxl@latest`, `python3Packages.pytest@latest` et `ruff@latest`, avec un `init_hook` affichant un message d'accueil en français.
- **Rationale** : Jetify Devbox s'appuie nativement sur Nixpkgs. En référençant directement `python3Packages.<paquet>`, Devbox construit un environnement strictement identique à celui de `flake.nix`, sans activer le plugin `venv` automatique qui imposerait l'usage de `pip`.
- **Alternatives considered** :
  - *Plugin Python `venv` de Devbox + `pip`* : Rejeté car rompt la symétrie avec `flake.nix` et contredit la décision de la clarification `FR-002` (zéro étape `pip` ou `.venv`).

## 3. Orchestration et bascule sans conflit dans `.envrc`

- **Decision** : Structurer `.envrc` autour d'un sélecteur piloté par la variable d'environnement `OUTIL_ENVIRONNEMENT` (valeurs acceptées : `auto`, `flake`, `devbox` ; valeur par défaut : `auto`) avec chargement optionnel préalable de `.envrc.local` (`source_env_if_exists .envrc.local`) :
  1. Si `OUTIL_ENVIRONNEMENT=flake` : vérifier `has nix`, exécuter `use flake`, afficher un message en français confirmant l'activation via Nix Flake (ou afficher une erreur en français si `nix` est absent).
  2. Si `OUTIL_ENVIRONNEMENT=devbox` : vérifier `has devbox`, activer l'environnement Devbox via `eval "$(devbox generate direnv --print-envrc)"`, afficher un message en français confirmant l'activation via Devbox (ou afficher une erreur en français si `devbox` est absent).
  3. Si `OUTIL_ENVIRONNEMENT=auto` (défaut) : tester d'abord `has nix` (priorité à `flake.nix`), sinon tester `has devbox` (repli automatique sur `devbox.json`), sinon afficher un message d'erreur explicite en français listant les prérequis manquants.
- **Rationale** : Garantit qu'un seul gestionnaire d'environnement est chargé à la fois, respecte la priorité à `flake.nix` choisie lors de la clarification `FR-004`, permet le repli automatique sur un poste n'ayant que Devbox, et offre une bascule immédiate sans modifier de fichier versionné.
- **Alternatives considered** :
  - *Commenter/décommenter manuellement `use flake` dans `.envrc`* : Rejeté lors de la clarification `FR-004` car salit l'état Git du dépôt à chaque test de bascule.

## 4. Compatibilité avec les fichiers d'export SGDF (`ExportIndividus.xls`)

- **Decision** : Inclure simultanément `pandas`, `beautifulsoup4`, `lxml`, `xlrd` et `openpyxl` dans les deux définitions d'environnement.
- **Rationale** : L'analyse du fichier `ExportIndividus.xls` présent dans le répertoire montre que l'intranet SGDF exporte des documents HTML encodés en texte sous l'extension `.xls`. `beautifulsoup4` et `lxml` permettent à `pandas.read_html` (ou à un parseur direct) de lire ces fichiers HTML-XLS, tandis que `xlrd` et `openpyxl` prennent en charge les vrais classeurs binaires `.xls` et `.xlsx`.
- **Alternatives considered** :
  - *Inclure uniquement `xlrd` ou `openpyxl`* : Rejeté car incapable de parser les exports HTML portant l'extension `.xls` générés par le portail SGDF.

## 5. Confidentialité des données (RGPD) et propreté du suivi de version

- **Decision** : Créer un fichier `.gitignore` à la racine excluant les dossiers techniques éphémères (`.direnv/`, `.devbox/`, `.envrc.local`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`) ainsi que tous les fichiers de données nominatives (`*.xls`, `*.xlsx`, `*.csv`, `ExportIndividus*`).
- **Rationale** : Empêche toute validation accidentelle des coordonnées des familles du groupe SGDF de La Rochelle et des caches d'environnement locaux, conformément au Principe IV de la constitution et à `FR-006`.
- **Alternatives considered** :
  - *Ignorer uniquement `ExportIndividus.xls` par son nom exact* : Rejeté car d'autres exports ou fichiers générés (`*.xls`, `*.xlsx`, `*.csv`) pourraient contenir des données personnelles et être ajoutés par erreur.
