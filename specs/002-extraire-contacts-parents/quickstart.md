# Guide de Démarrage et de Validation Rapide (`quickstart.md`)

**Branche** : `002-extraire-contacts-parents` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

Ce guide décrit les étapes permettant d'exécuter le script d'extraction des contacts parents SGDF et de vérifier la conformité du fichier `ContactsParents.xlsx` généré.

## 1. Prérequis

- Se placer dans le dossier du projet afin que `direnv` active automatiquement l'environnement éphémère Python 3 (`flake.nix` ou `devbox.json`).
- Disposer du fichier `ExportIndividus.xls` à la racine du projet.

## 2. Exécution standard du script

Lancer le script sans argument pour traiter `ExportIndividus.xls` et générer `ContactsParents.xlsx` :

```bash
python3 extraire_contacts_parents.py
```

**Résultat attendu** :
- Affichage d'un récapitulatif en français sur la sortie standard (nombre de jeunes traités, nombre de parents uniques extraits et chemin du fichier généré).
- Création du fichier `ContactsParents.xlsx` contenant les onglets `ExportIndividus` et `ContactsParents`.
- Le fichier d'entrée `ExportIndividus.xls` reste strictement inchangé.

## 3. Exécution avec chemins personnalisés

```bash
python3 extraire_contacts_parents.py --entree ExportIndividus.xls --sortie sorties/ContactsParents.xlsx
```

## 4. Validation automatisée (Tests et Qualité)

Exécuter la suite de tests unitaires et d'intégration ainsi que le vérificateur de code :

```bash
pytest -v
ruff check .
```

**Critères vérifiés par les tests** :
- Présence des 134 parents uniques dédoublonnés sur `(Nom, Prénom)` à partir de `ExportIndividus.xls`.
- Formatage strict `NOM` (majuscules) et `Prénom` (casse titre, y compris prénoms composés).
- Regroupement complet des fratries et normalisation des unités courtes (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`).
- Enrichissement automatique des 18 Parents Animateurs Farfadets et autres parents bénévoles (numéro d'adhérent + rôle dans `Remarques`) ainsi que des statuts `Pré-inscrit(e)` / `Invité(e)`.
- Tri alphabétique français (gestion des accents) sur `(Nom, Prénom)`.
- Intégrité SHA-256 intacte de `ExportIndividus.xls`.
