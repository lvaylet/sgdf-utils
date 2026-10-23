# Guide de Validation Rapide (`quickstart.md`)

**Branche** : `006-formater-noms-famille` | **Date** : 2026-10-23 | **Spécification** : [spec.md](./spec.md)

Ce guide permet de vérifier de bout en bout le formatage des noms de famille en minuscules avec la première lettre de chaque mot en majuscule (comme les prénoms) depuis `ExportIndividus.xls` jusqu'à `ContactsParents.xlsx` et `ContactParents.vcf`.

## 1. Prérequis

- Se placer à la racine du dépôt afin que `direnv` active automatiquement l'environnement éphémère Python 3 (`flake.nix` ou `devbox.json`).
- Disposer du fichier `ExportIndividus.xls` à la racine du projet (optionnel pour les tests synthétiques, requis pour la validation de bout en bout sur données réelles).

## 2. Exécution de bout en bout

1. **Extraire les contacts des parents dans `ContactsParents.xlsx`** :

   ```bash
   python3 extract_parent_contacts.py
   ```

   - Vérifier dans l'onglet `ContactsParents` que la colonne `Nom` et les noms de famille dans `Noms des enfants` sont formatés avec la première lettre de chaque mot/segment en majuscule et le reste en minuscules (ex. `Bernard`, `Dupont-Moretti`, `Lucas Bernard, Chloé Bernard`), voir [data-model.md](./data-model.md).

2. **Générer le fichier vCard `ContactParents.vcf`** :

   ```bash
   python3 generate_contacts_vcf.py
   ```

   - Vérifier que les lignes `N:`, `FN:` et `NOTE:Enfants : ...` dans `ContactParents.vcf` présentent les noms de famille des parents et des enfants en casse titre (`Prénom Nom`), conformément au [contrat de formatage](./contracts/contrat-formatage-noms.md).

## 3. Exécution des tests automatisés et du linter

```bash
pytest -v
ruff check .
```

**Résultats attendus** :

- 100 % des tests unitaires et d'intégration passent (`pytest -v`).
- Aucune erreur signalée par le vérificateur de code (`ruff check .`).
- Le fichier d'entrée `ExportIndividus.xls` demeure strictement intact (lecture seule vérifiée par empreinte SHA-256).
