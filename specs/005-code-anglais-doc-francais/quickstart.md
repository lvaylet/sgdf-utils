# Guide de Validation Rapide (Quickstart) : Code en Anglais, Commentaires en Français et Renommage en `README.md`

## 1. Prérequis

Se placer à la racine du dépôt avec l'environnement éphémère Nix / Devbox actif via `direnv`.

## 2. Vérifier le renommage de `LISEZMOI.md` en `README.md`

```bash
test -f README.md && test ! -f LISEZMOI.md
```

**Résultat attendu** : `README.md` existe à la racine, `LISEZMOI.md` n'existe plus, et le contenu de `README.md` est intégralement rédigé en français.

## 3. Vérifier le renommage des fichiers Python et l'absence des anciens fichiers en français

```bash
test -f extract_parent_contacts.py && test ! -f extraire_contacts_parents.py
test -f generate_contacts_vcf.py && test ! -f generer_contacts_vcf.py
test -f tests/test_environment.py && test ! -f tests/test_environnement.py
test -f tests/test_extract_parent_contacts.py && test ! -f tests/test_extraire_contacts_parents.py
test -f tests/test_generate_contacts_vcf.py && test ! -f tests/test_generer_contacts_vcf.py
```

## 4. Exécuter le flux métier complet de bout en bout

```bash
# 1. Extraire les contacts des parents depuis ExportIndividus.xls vers ContactsParents.xlsx
python3 extract_parent_contacts.py --input ExportIndividus.xls --output ContactsParents.xlsx

# 2. Générer ContactParents.vcf à partir de ContactsParents.xlsx
python3 generate_contacts_vcf.py --input ContactsParents.xlsx --output ContactParents.vcf
```

**Résultat attendu** :

- Messages d'exécution affichés en français.
- `ContactsParents.xlsx` généré avec 134 parents uniques et les 13 colonnes en français dans l'onglet `ContactsParents`.
- `ContactParents.vcf` généré avec 134 fiches `VCARD` 3.0 complètes.
- `ExportIndividus.xls` strictement intact (empreinte SHA-256 inchangée).

## 5. Exécuter la suite de tests automatisés et le contrôleur de qualité

```bash
pytest -v
ruff check .
```

**Résultat attendu** : 100 % des tests passent avec succès et `ruff check .` retourne `All checks passed!`.
