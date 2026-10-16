# Guide de Démarrage et de Validation Rapide (`quickstart.md`)

**Branche** : `001-env-dev-ephemere` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

Ce guide présente les scénarios de validation permettant de vérifier de bout en bout le bon fonctionnement de l'environnement de développement éphémère double option (`flake.nix` et `devbox.json`) activé par `.envrc`.

## 1. Prérequis sur le poste du bénévole

- `direnv` installé et accroché au shell (`eval "$(direnv hook bash)"` ou équivalent `zsh`/`fish`).
- Au moins l'un des deux outils suivants :
  - **Nix** avec les fonctionnalités `nix-command` et `flakes` activées.
  - **Jetify Devbox** (`devbox`).

## 2. Scénario 1 : Autorisation et activation automatique par défaut (`direnv`)

1. Se placer dans le dossier du projet et autoriser `.envrc` :
   ```bash
   direnv allow
   ```
2. Vérifier que le message d'activation s'affiche en français et que l'interpréteur Python 3 provient de l'environnement éphémère :
   ```bash
   which python3
   python3 --version
   ```
   **Résultat attendu** : Le chemin pointe vers le store Nix (`/nix/store/...`) ou le profil `.devbox`, et non vers `/usr/bin/python3`.

## 3. Scénario 2 : Vérification de la disponibilité des paquets et de la lecture de `ExportIndividus.xls`

1. Exécuter la suite de tests de validation de l'environnement :
   ```bash
   pytest
   ```
2. Vérifier la qualité du code avec `ruff` :
   ```bash
   ruff check .
   ```
3. Vérifier l'importation directe de toutes les bibliothèques requises (cf. [contrat-environnement.md](./contracts/contrat-environnement.md)) :
   ```bash
   python3 -c "import pandas, bs4, lxml, xlrd, openpyxl, pytest; print('Tous les paquets SGDF sont opérationnels.')"
   ```
   **Résultat attendu** : Code de retour `0`, aucune erreur `ModuleNotFoundError`, et confirmation en français.

## 4. Scénario 3 : Bascule entre `flake.nix` et `devbox.json` via `OUTIL_ENVIRONNEMENT`

1. Tester explicitement le mode Nix Flake :
   ```bash
   OUTIL_ENVIRONNEMENT=flake direnv reload
   ```
2. Tester explicitement le mode Jetify Devbox (si `devbox` est installé sur la machine) :
   ```bash
   OUTIL_ENVIRONNEMENT=devbox direnv reload
   ```
   *(Sur un poste ne disposant que de Nix, cette commande doit afficher un message d'avertissement clair en français indiquant que `devbox` n'est pas installé).*
3. Pour enregistrer une préférence locale permanente sans modifier les fichiers suivis par Git, créer un fichier `.envrc.local` :
   ```bash
   # Exemple dans .envrc.local (ignoré par Git)
   export OUTIL_ENVIRONNEMENT=devbox
   ```

## 5. Scénario 4 : Vérification du déchargement propre à la sortie du dossier

1. Quitter le répertoire du projet :
   ```bash
   cd ..
   ```
   **Résultat attendu** : `direnv: unloading` s'affiche et les paquets spécifiques au projet ne polluent plus l'environnement global de l'utilisateur (`SC-004`).
