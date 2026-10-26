# Guide de Validation Rapide (`quickstart.md`)

**Branche** : `007-extraire-package-sgdf-contacts` | **Date** : 2026-10-26 | **Spécification** : [spec.md](./spec.md)

Ce guide permet de vérifier l'extraction du cœur métier dans le package modulaire `sgdf_contacts/` ainsi que la rétrocompatibilité complète des scripts CLI `extract_parent_contacts.py` et `generate_contacts_vcf.py`.

## 1. Prérequis

- Se placer à la racine du dépôt afin que `direnv` active automatiquement l'environnement éphémère Python 3 (`flake.nix` ou `devbox.json`).

## 2. Vérification de l'API du package `sgdf_contacts` en mémoire

Exécuter une vérification rapide en mémoire (lecture `bytes`, propriété `waha_chat_id`, génération Excel `BytesIO` et génération vCard directe depuis `list[ParentContact]`) :

```bash
python3 -c '
import io
from sgdf_contacts.domain import ParentContact
from sgdf_contacts.parsers import read_individuals_export_table, extract_and_group_parents
from sgdf_contacts.exporters import write_parent_contacts_workbook, format_vcf_content

contact = ParentContact(last_name="Bernard", first_name="Élodie", primary_mobile_phone="+33687966975")
assert contact.waha_chat_id == "33687966975@c.us"
print("Validation waha_chat_id OK :", contact.waha_chat_id)
'
```

## 3. Exécution de bout en bout via les scripts CLI rétrocompatibles

1. **Extraire les contacts des parents dans `ContactsParents.xlsx`** :

   ```bash
   python3 extract_parent_contacts.py
   ```

2. **Générer le fichier vCard `ContactParents.vcf`** :

   ```bash
   python3 generate_contacts_vcf.py
   ```

## 4. Exécution des tests automatisés et du linter

```bash
pytest -v
ruff check .
```

**Résultats attendus** :

- 100 % des tests unitaires et d'intégration passent (`pytest -v`), incluant :
  - `tests/test_environment.py`
  - `tests/test_extract_parent_contacts.py`
  - `tests/test_generate_contacts_vcf.py`
  - `tests/test_sgdf_contacts_package.py`
- Aucune erreur signalée par le vérificateur de code (`ruff check .`).
- Aucune duplication de constantes ou de fonctions métier entre `extract_parent_contacts.py` et `generate_contacts_vcf.py`.
