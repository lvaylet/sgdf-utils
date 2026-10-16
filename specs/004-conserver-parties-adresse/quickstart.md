# Guide de Validation Rapide (`quickstart.md`)

**Branche** : `004-conserver-parties-adresse` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

Ce guide permet de vérifier de bout en bout la conservation des parties brutes de l'adresse (`Rue`, `Code postal`, `Ville`) depuis `ExportIndividus.xls` jusqu'à `ContactParents.vcf`.

## 1. Prérequis

- Se placer à la racine du dépôt afin que `direnv` active automatiquement l'environnement éphémère Python 3 (`flake.nix` ou `devbox.json`).
- Disposer du fichier `ExportIndividus.xls` à la racine du projet.

## 2. Exécution de bout en bout

1. **Extraire les contacts des parents dans `ContactsParents.xlsx`** :

   ```bash
   python3 extraire_contacts_parents.py
   ```

   - Vérifier que l'onglet `ContactsParents` de `ContactsParents.xlsx` contient désormais 13 colonnes : `Nom`, `Prénom`, `Téléphone portable principal`, `Téléphone portable secondaire`, `Téléphone fixe (domicile)`, `Adresse email`, `Noms des enfants`, `Unités des enfants`, `Rue`, `Code postal`, `Ville`, `Numéro d'adhérent`, `Remarques`.

2. **Générer le fichier vCard `ContactParents.vcf`** :

   ```bash
   python3 generer_contacts_vcf.py
   ```

   - Vérifier que `ContactParents.vcf` est généré sans erreur à partir des 13 colonnes de `ContactsParents.xlsx` et que les champs `ADR;TYPE=HOME:;;<rue>;<ville>;;<code_postal>;` reflètent directement les colonnes `Rue`, `Ville` et `Code postal`.

## 3. Exécution des tests automatisés et du linter

```bash
pytest -v
ruff check .
```

**Résultats attendus** :

- 100 % des tests unitaires et d'intégration passent (`pytest -v`).
- Aucune alerte de style ou de qualité (`ruff check .`).
- Les fichiers sources `ExportIndividus.xls` et `ContactsParents.xlsx` restent strictement intacts lors des lectures (vérifié par empreinte SHA-256).
