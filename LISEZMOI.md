# Automatisation SGDF La Rochelle — Contacts Parents

Ce dépôt accueille les scripts Python 3 destinés à automatiser les tâches administratives répétitives du groupe scout **Scouts et Guides de France (SGDF) de La Rochelle**, notamment le traitement des exports d'adhérents et des coordonnées des parents pour la mise à jour de **Google Contacts** et la préparation des **groupes WhatsApp d'unités**.

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

### Basculer entre `flake.nix` et `devbox.json`

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

## 3. Extraction et regroupement des contacts des parents (`extraire_contacts_parents.py`)

Le script `extraire_contacts_parents.py` lit en lecture seule le fichier d'export SGDF (`ExportIndividus.xls`) et génère le classeur Excel `ContactsParents.xlsx` comprenant :
1. L'onglet **`ExportIndividus`** : copie tabulaire fidèle des données d'origine.
2. L'onglet **`ContactsParents`** : liste des parents dédoublonnés sur `(Nom, Prénom)` et triés par ordre alphabétique français (Nom puis Prénom).

### Colonnes produites dans l'onglet `ContactsParents`

1. **`Nom`** : Nom de famille du parent en MAJUSCULES.
2. **`Prénom`** : Prénom du parent en minuscules avec initiale(s) en majuscule.
3. **`Téléphone portable principal`** : Numéro de portable principal au format international sans espaces (ex. `+33687966975`). Si ce champ est vide mais qu'un numéro de portable valide (`+336` ou `+337`) figure dans le téléphone fixe ou le portable secondaire, il y est automatiquement déplacé (avec priorité au téléphone fixe).
4. **`Téléphone portable secondaire`** : Numéro de portable secondaire au format international sans espaces.
5. **`Téléphone fixe (domicile)`** : Numéro de téléphone fixe domicile au format international sans espaces (ex. `+33546123456`).
6. **`Adresse email`** : Adresse courriel personnelle (ou dédiée SGDF en repli).
7. **`Noms des enfants`** : Liste des enfants regroupés sous la forme `Prénom NOM`, séparés par des virgules (ex. `Lucas BERNARD, Chloé BERNARD`).
8. **`Unités des enfants`** : Unités courtes des enfants dans le même ordre que les enfants eux-mêmes (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`).
9. **`Adresse physique`** : Adresse postale complète.
10. **`Numéro d'adhérent`** : Numéro d'adhérent SGDF du parent (issu de sa fiche représentant légal ou de son inscription adulte).
11. **`Remarques`** : Rôle éventuel du parent au sein du groupe (ex. `Parent Animateur Farfadet`, `Responsable de groupe`, délégations) et statut d'inscription des enfants s'il diffère de `Inscrit(e)` (`Pré-inscrit(e)` ou `Invité(e)`).

### Commandes d'utilisation

```bash
# Exécution standard (lit ExportIndividus.xls et génère ContactsParents.xlsx)
python3 extraire_contacts_parents.py

# Exécution avec chemins personnalisés
python3 extraire_contacts_parents.py --entree ExportIndividus.xls --sortie ContactsParents.xlsx

# Afficher l'aide en français
python3 extraire_contacts_parents.py --help
```

## 4. Vérification et tests

Une fois dans le dossier (avec l'environnement actif), vous pouvez vérifier le bon fonctionnement de l'installation et la conformité du code :

```bash
# Exécuter la suite de tests automatisés
pytest -v

# Vérifier la qualité et le style du code Python
ruff check .
```

## 5. Confidentialité des données (RGPD)

Conformément à la constitution du projet :
- Les fichiers d'export et de sortie (`ExportIndividus.xls`, `ContactsParents.xlsx`, `*.xls`, `*.xlsx`, `*.csv`) contiennent des données personnelles et sont **exclus du suivi Git** via `.gitignore`.
- Les scripts traitent toujours les exports originaux en **lecture seule**.
