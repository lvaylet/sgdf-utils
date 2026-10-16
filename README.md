# Automatisation SGDF La Rochelle — Contacts Parents

Ce dépôt accueille les scripts Python 3 destinés à automatiser les tâches administratives répétitives du groupe scout **Scouts et Guides de France (SGDF) de La Rochelle**, notamment le traitement des exports d'adhérents et des coordonnées des parents.

## 1. Environnement de développement éphémère

Pour éviter toute installation manuelle sur le système hôte et garantir la reproductibilité entre bénévoles, le projet fournit **deux définitions d'environnement éphémère maintenues en parallèle**, toutes deux activées automatiquement par `direnv` via le fichier `.envrc` :

1. **Option 1 — Nix Flakes (`flake.nix`)** : Option prioritaire par défaut lorsque `nix` est présent sur la machine.
2. **Option 2 — Jetify Devbox (`devbox.json`)** : Option de repli automatique lorsque seul `devbox` est présent, ou activable à la demande.

### Paquets et outils inclus d'office

Les deux options fournissent exactement le même environnement Python 3 isolé (sans étape `pip install` ni création de `.venv` requise) :

- **Python 3** (`python3`)
- **`pandas`** : Manipulation et croisement des tableaux d'adhérents et de parents
- **`beautifulsoup4`** et **`lxml`** : Analyse des exports SGDF au format HTML portant l'extension `.xls` (ex. `ExportIndividus.xls`)
- **`xlrd`** et **`openpyxl`** : Lecture et génération de classeurs Excel `.xls` et `.xlsx`
- **`pytest`** : Exécution des tests automatisés
- **`ruff`** : Vérification de la qualité et du style du code Python

## 2. Activation automatique avec `direnv`

Lors de votre première entrée dans le dossier, autorisez l'exécution du fichier `.envrc` :

```bash
direnv allow
```

Dès cet instant :

- À chaque entrée dans le dossier (`cd contacts-parents`), l'environnement Python 3 éphémère se charge automatiquement.
- À chaque sortie du dossier (`cd ..`), l'environnement est déchargé proprement sans laisser de trace sur le système hôte.

## 3. Basculer entre `flake.nix` et `devbox.json`

Le fichier `.envrc` s'adapte automatiquement aux outils installés sur votre poste via la variable `OUTIL_ENVIRONNEMENT` :

- **Comportement par défaut (`OUTIL_ENVIRONNEMENT=auto`)** : Utilise `flake.nix` si `nix` est installé, sinon bascule automatiquement sur `devbox.json` si `devbox` est installé.
- **Forcer l'utilisation de Nix Flakes (`flake.nix`)** :

  ```bash
  OUTIL_ENVIRONNEMENT=flake direnv reload
  ```

- **Forcer l'utilisation de Jetify Devbox (`devbox.json`)** :

  ```bash
  OUTIL_ENVIRONNEMENT=devbox direnv reload
  ```

- **Enregistrer votre préférence localement** (sans modifier les fichiers suivis par Git) : créez un fichier `.envrc.local` à la racine :

  ```bash
  echo "export OUTIL_ENVIRONNEMENT=devbox" > .envrc.local
  direnv allow
  ```

## 4. Vérification et tests

Une fois dans le dossier (avec l'environnement actif), vous pouvez vérifier le bon fonctionnement de l'installation et la conformité du code :

```bash
# Exécuter la suite de tests automatisés
pytest

# Vérifier la qualité et le style du code Python
ruff check .
```

Si vous utilisez directement les commandes de chaque outil :

- **Avec Nix Flakes** : `nix develop --command pytest`
- **Avec Devbox** : `devbox run tester` ou `devbox run verifier_qualite`

## 5. Confidentialité des données (RGPD)

Conformément à la constitution du projet :

- Les fichiers d'export issus de l'intranet SGDF (`ExportIndividus.xls`, `*.xls`, `*.xlsx`, `*.csv`) contiennent des données personnelles et sont **exclus du suivi Git** via `.gitignore`.
- Les scripts traitent toujours les exports originaux en **lecture seule**.
