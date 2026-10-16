# Contrat d'Interface de l'Environnement de Développement Éphémère

**Branche** : `001-env-dev-ephemere` | **Date** : 2026-10-16 | **Spécification** : [spec.md](../spec.md)

Ce document définit le contrat d'interface garanti aux bénévoles et aux scripts Python du projet lorsque l'environnement éphémère est activé, quelle que soit l'option retenue (`flake.nix` ou `devbox.json`).

## 1. Interface de Sélection et d'Activation (`.envrc`)

### Variables d'entrée supportées

| Variable | Valeurs autorisées | Valeur par défaut | Comportement garanti |
|----------|--------------------|-------------------|----------------------|
| `OUTIL_ENVIRONNEMENT` | `auto`, `flake`, `devbox` | `auto` | Détermine le gestionnaire d'environnement utilisé par `.envrc`. |

### Matrice de décision de `.envrc`

| `OUTIL_ENVIRONNEMENT` | `nix` installé | `devbox` installé | Résultat attendu |
|-----------------------|----------------|-------------------|------------------|
| `auto` (ou non défini) | Oui | Oui ou Non | Active `flake.nix` et affiche un message de confirmation en français. |
| `auto` (ou non défini) | Non | Oui | Active `devbox.json` en repli automatique et affiche un message de confirmation en français. |
| `auto` (ou non défini) | Non | Non | Affiche un message d'erreur explicite en français indiquant qu'au moins Nix ou Devbox est requis. |
| `flake` | Oui | Oui ou Non | Active `flake.nix` et affiche un message de confirmation en français. |
| `flake` | Non | Oui ou Non | Affiche un message d'erreur en français indiquant que Nix n'est pas disponible sur ce poste. |
| `devbox` | Oui ou Non | Oui | Active `devbox.json` et affiche un message de confirmation en français. |
| `devbox` | Oui ou Non | Non | Affiche un message d'erreur en français indiquant que Devbox n'est pas disponible sur ce poste. |
| Toute autre valeur | Oui ou Non | Oui ou Non | Affiche un message d'erreur en français listant les valeurs valides (`auto`, `flake`, `devbox`). |

## 2. Contrat des Exécutables et Bibliothèques Fournis

Une fois l'environnement activé (via `flake.nix` ou `devbox.json`), les exécutables et modules suivants DOIVENT être accessibles directement dans le `PATH` et le `PYTHONPATH` de l'environnement isolé :

### Exécutables en ligne de commande

| Commande | Rôle | Vérification |
|----------|------|--------------|
| `python3` (et `python`) | Interpréteur Python 3 isolé (fourni par Nix/Devbox) | `python3 --version` retourne `Python 3.x` et `which python3` pointe vers `/nix/store/...` ou `.devbox/...` |
| `pytest` | Exécuteur de tests unitaires et d'intégration | `pytest --version` retourne un code de sortie `0` |
| `ruff` | Vérificateur de style et de qualité de code Python | `ruff --version` retourne un code de sortie `0` |

### Bibliothèques Python pré-installées

| Nom du paquet | Module d'import Python | Usage dans le projet SGDF La Rochelle |
|---------------|------------------------|---------------------------------------|
| `pandas` | `import pandas` | Manipulation et croisement des tables d'adhérents et de contacts parents |
| `beautifulsoup4` | `import bs4` | Analyse des exports SGDF au format HTML portant l'extension `.xls` (`ExportIndividus.xls`) |
| `lxml` | `import lxml` | Moteur d'analyse HTML/XML rapide utilisé conjointement avec `beautifulsoup4` et `pandas` |
| `xlrd` | `import xlrd` | Lecture des classeurs Excel historiques au format binaire `.xls` |
| `openpyxl` | `import openpyxl` | Lecture et génération de classeurs Excel modernes au format `.xlsx` |
| `pytest` | `import pytest` | Écriture et exécution des tests automatisés en français |
